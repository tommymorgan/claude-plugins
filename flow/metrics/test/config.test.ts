import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
	type FlowConfig,
	generateSlug,
	readConfig,
	resolveConfig,
	writeConfig,
} from "../src/config.js";

describe("Slug generation", () => {
	it("should strip https protocol and normalize", () => {
		expect(generateSlug("https://github.com/infilla/infilla-app.git")).toBe(
			"github.com-infilla-infilla-app",
		);
	});

	it("should strip ssh protocol and normalize", () => {
		expect(generateSlug("git@github.com:infilla/infilla-app.git")).toBe(
			"github.com-infilla-infilla-app",
		);
	});

	it("should lowercase the result", () => {
		expect(generateSlug("https://GitHub.com/Infilla/Infilla-App.git")).toBe(
			"github.com-infilla-infilla-app",
		);
	});

	it("should strip .git suffix", () => {
		expect(generateSlug("https://github.com/tommy/homelab.git")).toBe(
			"github.com-tommy-homelab",
		);
	});

	it("should handle URLs without .git suffix", () => {
		expect(generateSlug("https://github.com/tommy/homelab")).toBe(
			"github.com-tommy-homelab",
		);
	});

	it("should handle Forgejo/Gitea URLs", () => {
		expect(generateSlug("https://code.tommymorgan.com/tommy/kizn.git")).toBe(
			"code.tommymorgan.com-tommy-kizn",
		);
	});
});

describe("Config persistence", () => {
	let tempDir: string;

	beforeEach(async () => {
		tempDir = await mkdtemp(join(tmpdir(), "flow-config-"));
	});

	afterEach(async () => {
		await rm(tempDir, { recursive: true, force: true });
	});

	const sampleConfig: FlowConfig = {
		remoteUrl: "git@github.com:infilla/infilla-app.git",
		source: "github",
		repos: ["infilla/infilla-app"],
		startedAt: "earliest_commit_authored_date",
		finishedAt: "pr_merged",
		createdAt: "2026-04-03T00:00:00Z",
	};

	it("should write and read config atomically", async () => {
		const slug = "github.com-infilla-infilla-app";
		await writeConfig(tempDir, slug, sampleConfig);
		const result = await readConfig(tempDir, slug);
		expect(result).toEqual(sampleConfig);
	});

	it("should return null for non-existent config", async () => {
		const result = await readConfig(tempDir, "does-not-exist");
		expect(result).toBeNull();
	});

	it("should resolve config by matching git remote URL", async () => {
		const slug = "github.com-infilla-infilla-app";
		await writeConfig(tempDir, slug, sampleConfig);

		const result = await resolveConfig(
			tempDir,
			"git@github.com:infilla/infilla-app.git",
		);
		expect(result).toEqual({ slug, config: sampleConfig });
	});

	it("should return null when no config matches the remote URL", async () => {
		await writeConfig(tempDir, "github.com-infilla-infilla-app", sampleConfig);

		const result = await resolveConfig(
			tempDir,
			"git@github.com:other/repo.git",
		);
		expect(result).toBeNull();
	});

	it("should report the unmatched remote URL when resolution fails", async () => {
		const result = await resolveConfig(
			tempDir,
			"git@github.com:unknown/repo.git",
		);
		expect(result).toBeNull();
	});
});
