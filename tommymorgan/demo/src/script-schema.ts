import { z } from "zod";

const NavigateAction = z.object({
  type: z.literal("navigate"),
  url: z.string(),
});

const ClickAction = z.object({
  type: z.literal("click"),
  selector: z.string(),
});

const FillAction = z.object({
  type: z.literal("fill"),
  selector: z.string(),
  value: z.string(),
});

const WaitAction = z.object({
  type: z.literal("wait"),
  duration: z.number(),
});

const ScrollAction = z.object({
  type: z.literal("scroll"),
  direction: z.enum(["up", "down"]),
  amount: z.number(),
});

const HoverAction = z.object({
  type: z.literal("hover"),
  selector: z.string(),
});

const ScreenshotAction = z.object({
  type: z.literal("screenshot"),
});

const HighlightAction = z.object({
  type: z.literal("highlight"),
  selector: z.string(),
});

const ActionSchema = z.discriminatedUnion("type", [
  NavigateAction,
  ClickAction,
  FillAction,
  WaitAction,
  ScrollAction,
  HoverAction,
  ScreenshotAction,
  HighlightAction,
]);

const VoiceSettingsSchema = z.object({
  name: z.string(),
  rate: z.string().optional(),
  pitch: z.string().optional(),
});

const SceneSchema = z.object({
  id: z.string(),
  narration: z.string(),
  actions: z.array(ActionSchema),
  transition: z.enum(["crossfade", "cut", "fade-to-black"]),
  voiceOverrides: VoiceSettingsSchema.partial().omit({ name: true }).optional(),
});

export const DemoScriptSchema = z.object({
  version: z.literal(1),
  name: z.string(),
  strategy: z.enum(["scene-based", "continuous", "screenshot"]),
  resolution: z.object({
    width: z.number(),
    height: z.number(),
  }),
  voice: VoiceSettingsSchema,
  scenes: z.array(SceneSchema),
});

export type DemoScript = z.infer<typeof DemoScriptSchema>;
export type Scene = z.infer<typeof SceneSchema>;
export type Action = z.infer<typeof ActionSchema>;
export type VoiceSettings = z.infer<typeof VoiceSettingsSchema>;
