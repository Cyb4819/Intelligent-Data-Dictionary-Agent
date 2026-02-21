"use client"

import Image from "next/image"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { useState } from "react"

export function AddDatabaseDialog() {
	const [open, setOpen] = useState(false)

	const onOpenChange = (newOpen: boolean) => {
		setOpen(newOpen)
	}

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {/* 
        The button that triggers the dialog.
        You can reuse this entire component in multiple places.
      */}
      <DialogTrigger asChild>
        <Button className="rounded-full gap-2 flex text-xs" variant={"outline"}>
          Add Database
        </Button>
      </DialogTrigger>

      {/* The dialog content */}
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Connect a Database</DialogTitle>
          <DialogDescription>
            Choose a database provider to integrate with your application.
          </DialogDescription>
        </DialogHeader>

        {/* Main content area, styled as a 2-column layout */}
        <div className="flex flex-col md:flex-row gap-4">
          {/* Left column: icons and database names */}
          <div className="md:w-1/2 border-r pr-4 space-y-2">
            {/* Postgres */}
            <Button variant="ghost" className="w-full justify-start py-4">
              <Image
                src="/postgres.svg"
                alt="Postgres"
                width={30}
                height={30}
                className="mr-2"
              />
              Postgres - <span className="text-xs ml-1 text-green-400">Connected</span>
            </Button>

            {/* Redis */}
            <Button variant="ghost" className="w-full justify-start py-4">
              <Image
                src="/redis.svg"
                alt="Redis"
                width={30}
                height={30}
                className="mr-2"
              />
              Redis
            </Button>
          
					  {/* Mysql */}
            <Button variant="ghost" className="w-full justify-start py-4">
              <Image
                src="/mysql.svg"
                alt="Redis"
                width={30}
                height={30}
                className="mr-2"
              />
              Mysql
            </Button>

            {/* Firebase */}
            <Button variant="ghost" className="w-full justify-start py-4">
              <Image
                src="/firebase.svg"
                alt="Firebase"
                width={30}
                height={30}
                className="mr-2"
              />
              Firebase
            </Button>

            {/* Mongo */}
            <Button variant="ghost" className="w-full justify-start py-4">
              <Image
                src="/mongo.svg"
                alt="Mongo"
                width={30}
                height={30}
                className="mr-2"
              />
              Mongo
            </Button>
           
					  {/* elastic */}
            <Button variant="ghost" className="w-full justify-start py-4">
              <Image
                src="/elastic.svg"
                alt="Mongo"
                width={30}
                height={30}
                className="mr-2"
              />
              Elastic Search
            </Button>

            {/* Custom */}
            <Button variant="ghost" className="w-full justify-start py-4">
              <Image
                src="/custom.svg"
                alt="My DB"
                width={30}
                height={30}
                className="mr-2"
              />
              My Custom DB
            </Button>
          </div>

          {/* Right column: explanation */}
          <div className="md:w-1/2 gap-2 p-4 flex flex-col justify-center">
            <h2 className="text-sm font-bold">What is a Database?</h2>
            <p className="text-sm text-muted-foreground">
              A database is a service that stores and organizes your data. Choose the provider
              that best suits your application’s needs.
            </p>
            <p className="text-sm text-muted-foreground">
              Once connected, you can manage data directly through our interface.
            </p>
						<Button className="rounded-full mt-6 self-center text-xs">Get a Database</Button>
          </div>
        </div>

        {/* Optional footer for actions (e.g., a "Close" or "Confirm" button) */}
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}