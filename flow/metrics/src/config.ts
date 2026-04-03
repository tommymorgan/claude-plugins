import { randomBytes } from "node:crypto";
import { mkdir, readdir, readFile, rename, writeFile } from "node:fs/promises";
import { join } from "node:path";

export type DataSource = "github" | "linear" | "git";

export interface FlowConfig {
	remoteUrl: string;
	source: DataSource;
	repos?: string[];
	team?: string;
	mainBranch?: string;
	startedAt: string;
	finishedAt: string;
	createdAt: string;
}

/**
 * Generate a filesystem-safe slug from a git remote URL.
 *
 * Strips protocol, replaces / and : with -, strips .git suffix, lowercases.
 */
export function generateSlug(remoteUrl: string): string {
	return remoteUrl
		.replace(/^https?:\/\//, "")
		.replace(/^git@/, "")
		.replace(/\.git$/, "")
		.replace(/[/:]/g, "-")
		.toLowerCase();
}

/**
 * Write a flow config atomically to the flows directory.
 */
export async function writeConfig(
	flowsDir: string,
	slug: string,
	config: FlowConfig,
): Promise<void> {
	await mkdir(flowsDir, { recursive: true });
	const filePath = join(flowsDir, `${slug}.json`);
	const tempFile = join(
		flowsDir,
		`.${slug}-${randomBytes(4).toString("hex")}.tmp`,
	);
	await writeFile(tempFile, JSON.stringify(config, null, 2), "utf-8");
	await rename(tempFile, filePath);
}

/**
 * Read a flow config by slug. Returns null if not found.
 */
export async function readConfig(
	flowsDir: string,
	slug: string,
): Promise<FlowConfig | null> {
	try {
		const content = await readFile(join(flowsDir, `${slug}.json`), "utf-8");
		return JSON.parse(content) as FlowConfig;
	} catch (err) {
		if ((err as NodeJS.ErrnoException).code === "ENOENT") return null;
		throw err;
	}
}

/**
 * Find a flow config that matches the given git remote URL.
 * Scans all config files in the flows directory.
 */
export async function resolveConfig(
	flowsDir: string,
	remoteUrl: string,
): Promise<{ slug: string; config: FlowConfig } | null> {
	let files: string[];
	try {
		files = await readdir(flowsDir);
	} catch (err) {
		if ((err as NodeJS.ErrnoException).code === "ENOENT") return null;
		throw err;
	}

	for (const file of files) {
		if (!file.endsWith(".json") || file.endsWith("-data.json")) continue;

		const content = await readFile(join(flowsDir, file), "utf-8");
		const config = JSON.parse(content) as FlowConfig;

		if (config.remoteUrl === remoteUrl) {
			const slug = file.replace(/\.json$/, "");
			return { slug, config };
		}
	}

	return null;
}
