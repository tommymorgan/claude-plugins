import { randomBytes } from "node:crypto";
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import type { FlowData } from "./types.js";

/**
 * Write flow data atomically: write to temp file, then rename.
 * Prevents data corruption from interrupted writes.
 */
export async function writeFlowData(
	filePath: string,
	data: FlowData,
): Promise<void> {
	const dir = dirname(filePath);
	await mkdir(dir, { recursive: true });

	const tempFile = join(
		dir,
		`.flow-data-${randomBytes(4).toString("hex")}.tmp`,
	);
	const json = JSON.stringify(data, null, 2);

	await writeFile(tempFile, json, "utf-8");
	await rename(tempFile, filePath);
}

/**
 * Read flow data from disk. Returns null if file does not exist.
 */
export async function readFlowData(filePath: string): Promise<FlowData | null> {
	try {
		const content = await readFile(filePath, "utf-8");
		return JSON.parse(content) as FlowData;
	} catch (err) {
		if ((err as NodeJS.ErrnoException).code === "ENOENT") {
			return null;
		}
		throw err;
	}
}
