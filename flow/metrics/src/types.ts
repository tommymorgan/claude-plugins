export interface WorkItem {
	id: number;
	title: string;
	author: string;
	startedAt: string; // ISO 8601
	finishedAt: string; // ISO 8601
	cycleTimeDays: number;
	repo: string;
	labels: string[];
}

export interface FlowData {
	updatedAt: string; // ISO 8601
	items: WorkItem[];
}

export interface FlowFilter {
	author?: string;
	repo?: string;
}
