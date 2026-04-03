import type { WorkItem } from "../types.js";

export interface OpenItem {
	id: number;
	title: string;
	author: string;
	startedAt: string;
	ageDays: number;
	source: string;
}

export interface FlowAdapter {
	fetchWorkItems(options?: { since?: string }): Promise<WorkItem[]>;
	fetchOpenItems(): Promise<OpenItem[]>;
}
