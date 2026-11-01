import { expect, test } from "@playwright/test";
import { installMocks } from "./mocks";

test.describe.configure({ timeout: 60_000 });

const freshLaunchPath = "/mcp?__e2eOnboarding=fresh";
const upgradeLaunchPath = "/mcp?__e2eOnboarding=upgrade";

test.beforeEach(async ({ page }) => {
	await installMocks(page);
});

test("closing before consent leaves the consent step for the next launch", async ({
	page,
}) => {
	await page.goto(freshLaunchPath);
	const wizard = page.getByRole("dialog", {
		name: "Welcome to model-toolbox",
	});

	await expect(wizard).toBeVisible();
	await expect(
		wizard.getByRole("button", { name: "MCP Servers" }),
	).toBeVisible();
	await expect(wizard.getByText(/What's new in/)).toHaveCount(0);

	await wizard.getByRole("button", { name: "Close" }).click();
	await expect(wizard).toBeHidden();

	await page.reload({ waitUntil: "domcontentloaded" });
	await expect(wizard).toBeVisible();
	await expect(
		wizard.getByRole("heading", { name: "Help improve model-toolbox" }),
	).toBeVisible();
	await expect(
		wizard.getByRole("button", { name: "MCP Servers" }),
	).toHaveCount(0);

	await wizard.getByRole("button", { name: "Start Working" }).click();
	await expect(wizard).toBeHidden();
	await page.reload({ waitUntil: "domcontentloaded" });
	await expect(wizard).toHaveCount(0);
});

test("fresh launch keeps release notes out of onboarding and persists consent", async ({
	page,
}) => {
	await page.goto(freshLaunchPath);
	const wizard = page.getByRole("dialog", {
		name: "Welcome to model-toolbox",
	});

	await expect(wizard).toBeVisible();
	await expect(wizard.getByText(/What's new in/)).toHaveCount(0);

	await wizard.getByRole("button", { name: "Next" }).click();
	await wizard.getByRole("button", { name: "Next" }).click();
	await wizard.getByRole("button", { name: "Next" }).click();

	const consent = wizard.getByRole("checkbox", {
		name: "Share anonymous usage data",
	});
	await expect(consent).not.toBeChecked();
	await wizard
		.getByText("Share anonymous usage data", { exact: true })
		.click();
	await expect(consent).toBeChecked();
	await wizard.getByRole("button", { name: "Get Started" }).click();
	await expect(wizard).toBeHidden();
	await expect(
		page.getByText("Everything starts in the sidebar"),
	).toBeVisible();

	await page.reload({ waitUntil: "domcontentloaded" });
	await expect(wizard).toHaveCount(0);
});

test("upgrade notes are acknowledged after the user sees them", async ({
	page,
}) => {
	await page.goto(upgradeLaunchPath);
	const wizard = page.getByRole("dialog", {
		name: "What's New in model-toolbox",
	});

	await expect(wizard).toBeVisible();
	await expect(wizard.getByText("What's new in 0.1.1")).toBeVisible();
	await expect(
		wizard
			.locator("[data-slot='modal-header']")
			.getByText(
				"ModelToolbox 0.1.1 fixes update checks so beta releases are resolved from the official lbxAOA/ModelToolbox repository.",
			),
	).toHaveCSS("font-weight", "400");
	await expect(wizard.getByRole("heading", { level: 4 })).toHaveText([
		"Fixes and maintenance",
		"Known issues",
	]);
	await expect(
		wizard.getByText(
			"ModelToolbox 0.1.1 fixes update checks so beta releases are resolved from the official lbxAOA/ModelToolbox repository.",
			{ exact: true },
		),
	).toBeVisible();
	await expect(
		wizard.getByRole("heading", {
			name: "Updates follow the official repository",
		}),
	).toBeVisible();

	await wizard.getByRole("button", { name: "Start Working" }).click();
	await expect(wizard).toBeHidden();

	await page.reload({ waitUntil: "domcontentloaded" });
	await expect(wizard).toHaveCount(0);
});

test("manual welcome replay preserves the release-note watermark", async ({
	page,
}) => {
	await page.goto("/settings?tab=application");
	await page.getByRole("button", { name: "Show Welcome" }).click();

	const wizard = page.getByRole("dialog", {
		name: "Welcome to model-toolbox",
	});
	await expect(wizard).toBeVisible();
	await wizard.getByRole("button", { name: "Close" }).click();
	await expect(wizard).toBeHidden();

	const watermark = await page.evaluate(() => {
		const stored = sessionStorage.getItem(
			"model-toolbox-e2e-store:default",
		);
		if (!stored) return null;
		return new Map(JSON.parse(stored)).get("lastSeenWhatsNewVersion");
	});
	expect(watermark).toBe("99.99.99");
});
