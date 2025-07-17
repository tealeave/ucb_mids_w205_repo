
Here’s a detailed, step-by-step breakdown of the eight “pro tricks” from the video, with every key command you’ll need:

---

## 1. Embed Your “claude.md” Rules File

**Why:** Forces Claude Code to think in tiny, verifiable tasks and keeps your code bug-free.
**How:**

1. Create a file named `claude.md` at the root of your project.
2. Copy in your personal “rules” (e.g. “Break every prompt into tasks; ask for approval before coding each task; log every task to its own folder,” etc.).
3. Save—Claude Code will automatically load and enforce these rules on every prompt.

---

## 2. Always Enter **Plan Mode** Before Coding

**Why:** Guarantees you get exactly what you asked for, every time.
**Commands:**

* **Enter plan mode:**

  ```
  Shift + Tab, Shift + Tab  
  ```
* **Specify model for planning:**

  ```
  /mod opus  
  ```

  *(Opus is optimized for outlining; generates better plans.)*
* **Example flow:**

  1. Shift+Tab × 2 → describe “Build a to-do list feature”
  2. Hit Enter → get back a step-by-step plan
  3. When you’re ready to code, switch model:

     ```
     /model sonnet  
     ```

  *(Sonnet is cheaper and perfect for execution.)*

---

## 3. Use GitHub as Your “Checkpoint” System

**Why:** Claude Code lacks rewind/checkpoints; Git commits fill that gap.
**Workflow:**

1. **After every successful micro-step:**

   ```bash
   git add .
   git commit -m "feat: completed [feature/task]"
   ```
2. **If Claude messes up:**

   ```bash
   git reset --hard HEAD^
   ```

   Then re-invoke Claude Code on that step.

---

## 4. Drag-and-Drop Screenshots for UI Inspiration & Bug-Fixing

**Why:** Claude can “see” your screenshots and generate/fix UI accordingly.
**How to Capture & Send:**

* **On macOS:**

  ```
  Cmd + Shift + 4  
  ```
* **In the chat:**

  1. Drag your `.png` into Claude Code
  2. Prompt:

     > “Build the UI seen in the screenshot I just sent.”
  3. Or for bugs:

     > “Fix the error shown in the screenshot.”

---

## 5. Clear Context Frequently with `/clear`

**Why:** Reduces hallucinations and token costs by wiping old context.
**When to `/clear`:**

* Immediately after Claude finishes each sizable task or feature.
* Before starting a brand-new micro-step.
  **Command:**

```
/clear
```

---

## 6. Run Security Checks on Every Feature

**Why:** Prevents shipping insecure code (exposed API keys, vulnerabilities).
**Workflow:**

1. After Claude completes a feature, send:

   > “Please check through all the code you just wrote and make sure it follows security best practices: no sensitive info in front end, no vulnerabilities exploitable by attackers.”
2. Review and approve Claude’s fixes before merging.

---

## 7. Learn What Claude Builds (“Explain Mode”)

**Why:** Even non-coders need to grasp data flow and logic to prompt better.
**Prompt:**

> “Please explain the functionality and code you just built out in detail. Walk me through what you changed and how it works, as if you’re a senior engineer teaching me.”

Use this **after** your security check to deepen your understanding.

---

## 8. Use Claude for “Idle-Time” Brainstorming

**Why:** Turns long code-generation waits into productive idea sessions.
**Setup Prompt (once):**

> “When I’m coding with AI, there are long breaks during which I usually doom-scroll. Instead, let’s use that time to chat: I’ll tell you what you’re building and what I’m thinking about, and you’ll help me brainstorm new ideas and next steps.”
> **During Waits:**

* Simply type “Hello, Claude” (or whatever your session name is) and start discussing business ideas, prompting improvements, etc., instead of grabbing your phone.

---

### Putting It All Together

1. **claude.md** → your seven golden rules
2. **Plan Mode** (`Shift + Tab × 2` → `/mod opus`)
3. **Execute** (`/model sonnet`)
4. **Git Commits** after each micro-step
5. **Drag + Drop** screenshots for UI/bug help
6. **/clear** often
7. **Security-check Prompt**
8. **Explain-mode Prompt**
9. **Idle-time Brainstorming Prompt**

Follow these in order for each new feature or bug-fix, and you’ll code faster, safer, and smarter with Claude Code.


```

```
### Use KIMI K2 with claude code

```{bash}
export ANTHROPIC_AUTH_TOKEN=sk-YOURKEY
export ANTHROPIC_BASE_URL=https://api.moonshot.ai/anthropic
```

