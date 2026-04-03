import { mkdtemp, readdir, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { readFlowData, writeFlowData } from "../src/storage.js";
import type { FlowData } from "../src/types.js";

describe("Flow data storage", () => {
	let tempDir: string;

	beforeEach(async () => {
		tempDir = await mkdtemp(join(tmpdir(), "flow-metrics-"));
	});

	afterEach(async () => {
		await rm(tempDir, { recursive: true, force: true });
	});

	const sampleData: FlowData = {
		updatedAt: "2026-04-01T10:00:00Z",
		items: [
			{
				id: 1,
				title: "Add login feature",
				author: "tommy",
				startedAt: "2026-01-01T10:00:00Z",
				finishedAt: "2026-01-03T15:00:00Z",
				cycleTimeDays: 3,
				repo: "infilla-app",
				labels: ["feature"],
			},
		],
	};

	it("should write data atomically (no partial writes)", async () => {
		const filePath = join(tempDir, "flow-data.json");
		await writeFlowData(filePath, sampleData);

		const result = await readFlowData(filePath);
		expect(result).toEqual(sampleData);

		// No temp files should remain
		const files = await readdir(tempDir);
		expect(files).toEqual(["flow-data.json"]);
	});

	it("should create parent directories if they do not exist", async () => {
		const filePath = join(tempDir, "nested", "dir", "flow-data.json");
		await writeFlowData(filePath, sampleData);

		const result = await readFlowData(filePath);
		expect(result).toEqual(sampleData);
	});

	it("should return null when file does not exist", async () => {
		const filePath = join(tempDir, "nonexistent.json");
		const result = await readFlowData(filePath);
		expect(result).toBeNull();
	});

	it("should overwrite existing data", async () => {
		const filePath = join(tempDir, "flow-data.json");
		await writeFlowData(filePath, sampleData);

		const updated: FlowData = {
			...sampleData,
			updatedAt: "2026-04-02T10:00:00Z",
			items: [
				...sampleData.items,
				{
					id: 2,
					title: "Fix bug",
					author: "alice",
					startedAt: "2026-02-01T10:00:00Z",
					finishedAt: "2026-02-05T15:00:00Z",
					cycleTimeDays: 5,
					repo: "infilla-app",
					labels: ["bug"],
				},
			],
		};
		await writeFlowData(filePath, updated);

		const result = await readFlowData(filePath);
		expect(result?.items.length).toBe(2);
	});
});
