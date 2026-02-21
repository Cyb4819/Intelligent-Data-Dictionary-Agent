package com.hackfest_2.data_dictionary_agent.controller;

import com.hackfest_2.data_dictionary_agent.service.MetadataService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/metadata")
@CrossOrigin(origins = "http://localhost:3000")
public class MetadataController {

    private final MetadataService metadataService;

    public MetadataController(MetadataService metadataService) {
        this.metadataService = metadataService;
    }

    @PostMapping("/extract")
    public List<Map<String, Object>> extractMetadata(
            @RequestBody List<Map<String, String>> sources) {


        return metadataService.extractFromMultipleSources(sources);
    }
}