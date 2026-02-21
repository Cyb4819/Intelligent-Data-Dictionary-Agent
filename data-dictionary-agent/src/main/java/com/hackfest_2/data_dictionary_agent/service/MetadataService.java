package com.hackfest_2.data_dictionary_agent.service;

import com.opencsv.CSVReader;
import com.opencsv.CSVReaderBuilder;
import org.springframework.stereotype.Service;

import java.io.*;
import java.sql.*;
import java.util.*;

@Service
public class MetadataService {

    // For MySQL
    public List<Map<String, Object>> extractMetadata(
            String url, String username, String password, String driverClassName) throws Exception {

        Class.forName(driverClassName);

        List<Map<String, Object>> tablesList = new ArrayList<>();

        try (Connection connection = DriverManager.getConnection(url, username, password)) {

            DatabaseMetaData metaData = connection.getMetaData();
            ResultSet tables = metaData.getTables(null, null, "%", new String[]{"TABLE"});

            while (tables.next()) {
                String tableName = tables.getString("TABLE_NAME");

                Map<String, Object> tableData = new HashMap<>();
                tableData.put("tableName", tableName);
                tableData.put("tableType", tables.getString("TABLE_TYPE"));

                // Row Count
                try (Statement statement = connection.createStatement();
                     ResultSet rowCount = statement.executeQuery("SELECT COUNT(*) FROM " + tableName)) {

                    rowCount.next();
                    tableData.put("rowCount", rowCount.getLong(1));
                }

                // Unique Columns
                ResultSet indexInfo = metaData.getIndexInfo(null, null, tableName, true, false);
                Set<String> uniqueColumns = new HashSet<>();
                while (indexInfo.next()) {
                    String column = indexInfo.getString("COLUMN_NAME");
                    if (column != null) uniqueColumns.add(column);
                }
                indexInfo.close();

                // Columns
                ResultSet columns = metaData.getColumns(null, null, tableName, null);
                List<Map<String, Object>> columnList = new ArrayList<>();

                while (columns.next()) {
                    Map<String, Object> columnData = new HashMap<>();

                    String columnName = columns.getString("COLUMN_NAME");

                    columnData.put("columnName", columnName);
                    columnData.put("dataType", columns.getString("TYPE_NAME"));
                    columnData.put("size", columns.getInt("COLUMN_SIZE"));
                    columnData.put("nullable",
                            columns.getInt("NULLABLE") == DatabaseMetaData.columnNullable);
                    columnData.put("defaultValue", columns.getString("COLUMN_DEF"));
                    columnData.put("autoIncrement", columns.getString("IS_AUTOINCREMENT"));
                    columnData.put("ordinalPosition", columns.getShort("ORDINAL_POSITION"));
                    columnData.put("isUnique", uniqueColumns.contains(columnName));

                    columnList.add(columnData);
                }

                tableData.put("columns", columnList);

                // Primary Keys
                ResultSet pk = metaData.getPrimaryKeys(null, null, tableName);
                List<String> primaryKeys = new ArrayList<>();
                while (pk.next()) {
                    primaryKeys.add(pk.getString("COLUMN_NAME"));
                }
                tableData.put("primaryKeys", primaryKeys);

                // Foreign Keys
                ResultSet fk = metaData.getImportedKeys(null, null, tableName);
                List<Map<String, String>> foreignKeys = new ArrayList<>();
                while (fk.next()) {
                    Map<String, String> fkData = new HashMap<>();
                    fkData.put("fkColumn", fk.getString("FKCOLUMN_NAME"));
                    fkData.put("pkTable", fk.getString("PKTABLE_NAME"));
                    fkData.put("pkColumn", fk.getString("PKCOLUMN_NAME"));
                    foreignKeys.add(fkData);
                }
                tableData.put("foreignKeys", foreignKeys);

                tablesList.add(tableData);
            }
        }

        Map<String, Object> sourceData = new HashMap<>();
        sourceData.put("connectionUrl", url);
        sourceData.put("userName", username);
        sourceData.put("password", password != null ? "*****" : null);
        sourceData.put("driverClassName", driverClassName);
        sourceData.put("tablesList", tablesList);

        return Collections.singletonList(sourceData);
    }

    // Multi-source extraction
    public List<Map<String, Object>> extractFromMultipleSources(List<Map<String, String>> sources) {
        List<Map<String, Object>> allSourcesData = new ArrayList<>();

        for (Map<String, String> source : sources) {
            try {
                String type = source.get("type");
                String name = source.getOrDefault("name", "Unknown");

                Map<String, Object> sourceData;

                switch (type.toLowerCase()) {
                    case "mysql":
                    case "postgres":
                    case "sqlite":
                        sourceData = extractFromJdbcSource(source);
                        break;
                    case "snowflake":
                        sourceData = extractFromSnowflake(source);
                        break;
                    case "csv":
                        sourceData = extractFromCsvFolder(source);
                        break;
                    default:
                        sourceData = createErrorSource(source);
                        break;
                }

                // ADD SOURCE NAME FOR UI
                if (sourceData.containsKey("tablesList")) {
                    ((Map) sourceData).put("sourceName", name);
                }
                allSourcesData.add(sourceData);

            } catch (Exception e) {
                allSourcesData.add(createErrorSource(source));
            }
        }
        return allSourcesData;
    }

    private Map<String, Object> extractFromJdbcSource(Map<String, String> source) throws Exception {
        String url = source.get("url");
        String username = source.get("username");
        String password = source.get("password");
        String driverClassName = source.get("driverClassName");

        Class.forName(driverClassName);
        List<Map<String, Object>> tablesList = new ArrayList<>();

        try (Connection connection = DriverManager.getConnection(url, username, password)) {
            DatabaseMetaData metaData = connection.getMetaData();
            ResultSet tables = metaData.getTables(null, null, "%", new String[]{"TABLE"});

            while (tables.next()) {
                String tableName = tables.getString("TABLE_NAME");

                Map<String, Object> tableData = new HashMap<>();
                tableData.put("tableName", tableName);
                tableData.put("tableType", tables.getString("TABLE_TYPE"));

                // Row Count of table
                try (Statement statement = connection.createStatement();
                     ResultSet rowCount = statement.executeQuery("select count(*) from " + tableName)) {
                    rowCount.next();
                    tableData.put("rowCount", rowCount.getLong(1));
                }

                // Unique Columns
                ResultSet indexInfo = metaData.getIndexInfo(null, null, tableName, true, false);
                HashSet<String> uniqueColumnNames = new HashSet<>();
                while (indexInfo.next()) {
                    String column = indexInfo.getString("COLUMN_NAME");
                    if (column != null) uniqueColumnNames.add(column);
                }
                indexInfo.close();

                // Columns
                ResultSet columns = metaData.getColumns(null, null, tableName, null);
                List<Map<String, Object>> columnList = new ArrayList<>();
                while (columns.next()) {
                    Map<String, Object> columnData = new HashMap<>();
                    String columnName = columns.getString("COLUMN_NAME");
                    columnData.put("columnName", columnName);
                    columnData.put("dataType", columns.getString("TYPE_NAME"));
                    columnData.put("size", columns.getInt("COLUMN_SIZE"));
                    columnData.put("nullable", columns.getInt("NULLABLE") == DatabaseMetaData.columnNullable);
                    columnData.put("defaultValue", columns.getString("COLUMN_DEF"));
                    columnData.put("autoIncrement", columns.getString("IS_AUTOINCREMENT"));
                    columnData.put("ordinalPosition", columns.getShort("ORDINAL_POSITION"));
                    columnData.put("isUnique", uniqueColumnNames.contains(columnName));
                    columnList.add(columnData);
                }

                tableData.put("columns", columnList);

                // Primary Keys
                ResultSet pk = metaData.getPrimaryKeys(null, null, tableName);
                List<String> primaryKeys = new ArrayList<>();
                while (pk.next()) {
                    primaryKeys.add(pk.getString("COLUMN_NAME"));
                }
                tableData.put("primaryKeys", primaryKeys);

                // Foreign Keys
                ResultSet fk = metaData.getImportedKeys(null, null, tableName);
                List<Map<String, String>> foreignKeys = new ArrayList<>();
                while (fk.next()) {
                    Map<String, String> fkData = new HashMap<>();
                    fkData.put("fkColumn", fk.getString("FKCOLUMN_NAME"));
                    fkData.put("pkTable", fk.getString("PKTABLE_NAME"));
                    fkData.put("pkColumn", fk.getString("PKCOLUMN_NAME"));
                    foreignKeys.add(fkData);
                }
                tableData.put("foreignKeys", foreignKeys);

                tablesList.add(tableData);
            }
        }

        Map<String, Object> sourceData = new HashMap<>();
        sourceData.put("connectionUrl", url);
        sourceData.put("userName", username);
        sourceData.put("password", password != null ? "*****" : null); // Hide password
        sourceData.put("driverClassName", driverClassName);
        sourceData.put("tablesList", tablesList);
        return sourceData;
    }

    private Map<String, Object> extractFromSnowflake(Map<String, String> source) throws Exception {
        String url = source.get("url");
        String username = source.get("username");
        String password = source.get("password");

        Class.forName("net.snowflake.client.jdbc.SnowflakeDriver");
        List<Map<String, Object>> tablesList = new ArrayList<>();

        try (Connection connection = DriverManager.getConnection(url, username, password)) {
            // Snowflake
            String sql = """
                SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """;

            try (Statement stmt = connection.createStatement();
                 ResultSet rs = stmt.executeQuery(sql)) {

                while (rs.next()) {
                    String tableName = rs.getString("TABLE_NAME");
                    Map<String, Object> tableData = new HashMap<>();
                    tableData.put("tableName", tableName);
                    tableData.put("tableType", rs.getString("TABLE_TYPE"));

                    // Row count
                    String countSql = "SELECT COUNT(*) FROM " + tableName;
                    try (ResultSet countRs = stmt.executeQuery(countSql)) {
                        countRs.next();
                        tableData.put("rowCount", countRs.getLong(1));
                    }

                    // Columns
                    List<Map<String, Object>> columns = new ArrayList<>();
                    String descSql = "DESC TABLE " + tableName;
                    try (ResultSet colRs = stmt.executeQuery(descSql)) {
                        int pos = 1;
                        while (colRs.next()) {
                            Map<String, Object> col = new HashMap<>();
                            col.put("columnName", colRs.getString("name"));
                            col.put("dataType", colRs.getString("type"));
                            col.put("size", 255); // Default
                            col.put("nullable", true);
                            col.put("defaultValue", null);
                            col.put("autoIncrement", "NO");
                            col.put("ordinalPosition", pos++);
                            col.put("isUnique", false);
                            columns.add(col);
                        }
                    }
                    tableData.put("columns", columns);
                    tableData.put("primaryKeys", new ArrayList<>());
                    tableData.put("foreignKeys", new ArrayList<>());

                    tablesList.add(tableData);
                }
            }
        }

        Map<String, Object> sourceData = new HashMap<>();
        sourceData.put("connectionUrl", url);
        sourceData.put("userName", username);
        sourceData.put("password", "*****");
        sourceData.put("driverClassName", "net.snowflake.client.jdbc.SnowflakeDriver");
        sourceData.put("tablesList", tablesList);
        return sourceData;
    }

    private Map<String, Object> extractFromCsvFolder(Map<String, String> source) {
        String path = source.get("path");
        List<Map<String, Object>> tablesList = new ArrayList<>();

        File folder = new File(path);
        File[] csvFiles = folder.listFiles((dir, name) -> name.endsWith(".csv"));

        if (csvFiles != null) {
            for (File csvFile : csvFiles) {
                Map<String, Object> tableData = new HashMap<>();
                String tableName = csvFile.getName().replace(".csv", "");
                tableData.put("tableName", tableName);
                tableData.put("tableType", "CSV_TABLE");
                tableData.put("rowCount", countCsvRows(csvFile));

                List<Map<String, Object>> columns = inferCsvColumns(csvFile);
                tableData.put("columns", columns);
                tableData.put("primaryKeys", new ArrayList<>());
                tableData.put("foreignKeys", new ArrayList<>());

                tablesList.add(tableData);
            }
        }

        Map<String, Object> sourceData = new HashMap<>();
        sourceData.put("connectionUrl", path);
        sourceData.put("userName", "N/A");
        sourceData.put("password", "N/A");
        sourceData.put("driverClassName", "CSV");
        sourceData.put("tablesList", tablesList);
        return sourceData;
    }

    // CSV
    private long countCsvRows(File file) {
        try (BufferedReader br = new BufferedReader(new FileReader(file))) {
            return br.lines().count() - 1;
        } catch (Exception e) {
            return 0;
        }
    }

    private List<Map<String, Object>> inferCsvColumns(File csvFile) {
        List<Map<String, Object>> columns = new ArrayList<>();
        try (CSVReader csvReader = new CSVReaderBuilder(new FileReader(csvFile)).build()) {
            String[] headers = csvReader.readNext();
            if (headers != null) {
                for (int i = 0; i < headers.length; i++) {
                    Map<String, Object> col = new HashMap<>();
                    col.put("columnName", headers[i].trim());
                    col.put("dataType", "VARCHAR");
                    col.put("size", 255);
                    col.put("nullable", true);
                    col.put("defaultValue", null);
                    col.put("autoIncrement", "NO");
                    col.put("ordinalPosition", i + 1);
                    col.put("isUnique", false);
                    columns.add(col);
                }
            }
        } catch (Exception e) {
            // Fallback
        }
        return columns;
    }

    private Map<String, Object> createErrorSource(Map<String, String> source) {
        Map<String, Object> errorData = new HashMap<>();
        errorData.put("connectionUrl", source.get("url"));
        errorData.put("userName", source.get("username"));
        errorData.put("password", "error");
        errorData.put("driverClassName", source.get("type"));
        errorData.put("tablesList", new ArrayList<>());
        return errorData;
    }
}
