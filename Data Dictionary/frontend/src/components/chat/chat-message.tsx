import { CheckIcon, CopyIcon } from "@radix-ui/react-icons";
import { ChatRequestOptions } from "ai";
import { Message } from "ai/react";
import { motion } from "framer-motion";
import { CheckCircle, RefreshCcw } from "lucide-react";
import { memo, useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import ButtonWithTooltip from "../button-with-tooltip";
import { Button } from "../ui/button";
import { useEffect, useRef } from 'react';
import { Player } from '@lordicon/react';

import {
	ChatBubble,
	ChatBubbleAvatar,
	ChatBubbleMessage,
} from "../ui/chat/chat-bubble";
import ChartSimple from "./ChartSimple";
import SendResultDialog from "./SendResultDialog";

export type ChatMessageProps = {
	message: Message;
	isLast: boolean;
	isLoading: boolean | undefined;
	reload: (chatRequestOptions?: ChatRequestOptions) => Promise<string | null | undefined>;
	addToolResult?: (args: { toolCallId: string; result: string }) => void;
};

const MOTION_CONFIG = {
	initial: { opacity: 0, scale: 1, y: 20, x: 0 },
	animate: { opacity: 1, scale: 1, y: 0, x: 0 },
	exit: { opacity: 0, scale: 1, y: 20, x: 0 },
	transition: {
		opacity: { duration: 0.1 },
		layout: {
			type: "spring",
			bounce: 0.3,
			duration: 0.2,
		},
	},
};

// ---------------- HELPER COMPONENTS ----------------

function SendCompleteCard({ result, action }: { result: string; action: string }) {
	const [dialogOpen, setDialogOpen] = useState(false);

	return (
		<div className="w-full my-6 bg-card text-card-foreground border border-card-border p-6 rounded-lg shadow-md">
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-2">
					<p className="font-semibold text-sm">{action} complete</p>
					<CheckCircle className="w-4 h-4" />
				</div>
				<SendResultDialog open={dialogOpen} onOpenChange={setDialogOpen} result={result} />
			</div>
			<p className="text-xs text-text-success">
				Your {action} was processed successfully.
			</p>
		</div>
	);
}


function SendProcessCard({ toolName }: { toolName: string }) {

	const ICON = require('./rook.json');

	const playerRef = useRef<Player>(null);

	useEffect(() => {
		playerRef.current?.playFromBeginning();
	}, [])

	return (
		<div className="w-full my-6 bg-card text-card-foreground border border-card-border p-6 rounded-lg shadow-md">
			<div className="flex items-center">
				<div className="flex items-center gap-2">
					<Player
						icon={ICON}
						ref={playerRef}
						size={20}
						onComplete={() => {
							setTimeout(() => {
								playerRef.current?.playFromBeginning();
							}, 800);
						}}
					/>
					<p className="font-semibold text-sm">{toolName} is running...</p>
				</div>
			</div>
			<p className="text-xs mt-2 text-text-success">
				The tool {toolName} is currently processing your request.
			</p>
		</div>
	);
}
// ---------------- MAIN COMPONENT ----------------

function ChatMessage({ message, isLast, isLoading, reload }: ChatMessageProps) {
	const [isCopied, setIsCopied] = useState<boolean>(false);

	const handleCopy = () => {
		navigator.clipboard.writeText(message.content);
		setIsCopied(true);
		setTimeout(() => setIsCopied(false), 1500);
	};



	const renderParts = () => {
		return message.parts?.map((part, index) => {
			switch (part.type) {
				case "text":
					return (
						<Markdown
							key={index}
							remarkPlugins={[remarkGfm]}
							components={{
								p: ({ node, ...props }) => (
									<p className="my-2" {...props} />
								),
								ul: ({ node, ...props }) => (
									<ul className="list-disc pl-5 -my-6" {...props} />
								),
								li: ({ node, ...props }) => (
									<li className="-my-2" {...props} />
								),
								code({
									node,
									inline,
									className,
									children,
									...props
								}: {
									node: any
									inline: boolean
									className: string
									children: any
									[key: string]: any
								}) {
									const isBlock = !inline
									if (isBlock) {
										return (
											<pre className="bg-accent text-accent-foreground p-6 rounded-md overflow-auto my-2" {...props}>
												<code>{children}</code>
											</pre>
										)
									}
									return (
										<code className="bg-accent text-accent-foreground px-1 py-0.5 rounded" {...props}>
											{children}
										</code>
									)
								},
								a: ({ node, href, children, ...props }) => {
									const isMailTo = href?.startsWith("mailto:")
									return (
										<a
											href={href}
											className={`underline text-blue-500"
												}`}
											{...props}
										>
											{children}
										</a>
									)
								},
							}}
						>
							{part.text}
						</Markdown>
					);
				case "tool-invocation": {
					const { toolCallId, toolName, state, result } = part.toolInvocation as { toolCallId: string; toolName: string; state: string; result?: string };
					// Handle partial states and complete call here


					if (state === "partial-call" || state === "call") {
						return (
							<div key={toolCallId}>
								<SendProcessCard toolName={toolName} />
							</div>
						);
					}


					if (toolName === "displayResults") {
						switch (state) {
							case "partial-call":
							case "call":
								return (
									<div key={toolCallId}>
										<SendProcessCard toolName={toolName} />
									</div>
								);
								interface DisplayResultsData {
									data: { x: string; y: number }[];
									title: string;
									description: string;
								}

							case "result": {
								const displayResult = result as unknown as DisplayResultsData;
								console.log("Display result", displayResult.data);
								return (
									<div key={toolCallId} className="my-6">
										<ChartSimple
											data={displayResult.data}
											chartTitle={displayResult.title}
											chartDescription={displayResult.description}
										/>
									</div>
								);
							}
						}
					}


					if (state === "result") {
						// Specific handling for queryDatabase
						if (toolName === "queryDatabase") {
							return (
								<div key={toolCallId} className="mt-2">
									<SendCompleteCard result={result as string} action="Query Database" />
								</div>
							);
						}

						if (toolName === "selectTable") {
							return (
								<div key={toolCallId} className="mt-2">
									<SendCompleteCard result={result as string} action="Select Table" />
								</div>
							);
						}

						// Fallback for other tools
						return (
							<div key={toolCallId} className="mt-2">
								{`${toolName} result: ${result}`}
							</div>
						);
					}
					return null;
				}
				default:
					return null;
			}
		});
	};

	const renderActionButtons = () =>
		message.role === "assistant" && (
			<div className="pt-4 flex gap-1 items-center text-muted-foreground">
				{!isLoading && (
					<ButtonWithTooltip side="bottom" toolTipText="Copy">
						<Button onClick={handleCopy} variant="ghost" size="icon" className="h-4 w-4">
							{isCopied ? (
								<CheckIcon className="w-3.5 h-3.5 transition-all" />
							) : (
								<CopyIcon className="w-3.5 h-3.5 transition-all" />
							)}
						</Button>
					</ButtonWithTooltip>
				)}
				{!isLoading && isLast && (
					<ButtonWithTooltip side="bottom" toolTipText="Regenerate">
						<Button
							variant="ghost"
							size="icon"
							className="h-4 w-4"
							onClick={() => reload()}
						>
							<RefreshCcw className="w-3.5 h-3.5 scale-100 transition-all" />
						</Button>
					</ButtonWithTooltip>
				)}
			</div>
		);

	return (
		<motion.div {...MOTION_CONFIG} className="flex flex-col gap-2 whitespace-pre-wrap">
			<ChatBubble variant={message.role === "user" ? "sent" : "received"}>
				{message.role === "assistant" && (
					<ChatBubbleAvatar
						src={message.role === "assistant" ? "/blue_logo_bold.svg" : ""}
						width={6}
						height={6}
						className="object-contain"
					/>
				)}
				<ChatBubbleMessage>
					{renderParts()}
					{renderActionButtons()}
				</ChatBubbleMessage>
			</ChatBubble>
		</motion.div>
	);
}

export default memo(
	ChatMessage,
	(prevProps, nextProps) => {
		if (nextProps.isLast) return false;
		return (
			prevProps.isLast === nextProps.isLast &&
			prevProps.message === nextProps.message
		);
	}
);
