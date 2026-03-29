---
name: tommymorgan:copy
description: Copy the last assistant output to the clipboard
allowed-tools: ["Bash"]
---

# Copy Last Output

Copy your most recent text output (the last message you sent to the user before this command was invoked) to the system clipboard using `xclip`.

## Instructions

1. Recall your last text response to the user (the message immediately before they typed `/tommymorgan:copy`)
2. Pipe it to `xclip -selection clipboard` via a heredoc
3. Report "Copied to clipboard"

If `xclip` is not available, try `xsel --clipboard --input` as a fallback. If neither is available, report the error.
