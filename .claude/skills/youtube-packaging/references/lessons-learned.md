# Lessons learned (Explore AI with Gopal)

One row per post-publish review. Newest at the bottom. Benchmarks for a new
channel: click-through roughly 4–6%.

| Date | Video | Click-through | Avg view duration | Key lesson |
|---|---|---|---|---|
| 2026-10-12 | Stop Building One AI Agent (ADK sub-agents) | 2.3% | 2:04 (16.6%) | Cluttered slide-style thumbnail and a "last video / basics" intro. Body content held viewers well |

## 2026-10-12 · Stop Building One AI Agent (Google ADK sub-agents)

Source: `video-projects/multi-agents/post-publish/post-publish-feedback-multi-agent.md`.
Video: https://youtu.be/ePEOffx_g7k (12:33). Stats 11 days after publish.

| Metric | Value | Read |
|---|---|---|
| Impressions | 1.1k, almost all in the first 2 days, then flat | YouTube tested it, then stopped pushing it |
| Click-through | 2.3% | Too low |
| Views / unique viewers | 64 / 23 | Inflated by repeat and own views |
| Engaged views | 39 | |
| Avg view duration | 2:04 (16.6%) | Low |
| Retention | ~85% → ~30% in the first 30–40s, then flat ~20% to the end | The intro loses people; the body holds the ones who stay |
| Traffic | Browse 35.9%, Search 29.7%, Suggested 14.1%, Channel 10.9%, Other 9.4% | Search demand exists; most viewers are new |

**Not the problem:** production quality, the HyperFrames motion graphics, the
teaching body (flat retention after the intro proves it).

**Packaging failed.** The thumbnail was a slide: ~60 words, two full diagrams,
two logos, tool lists. At phone size only the headline was readable, and it
repeated the title. Labels didn't match the video ("Product Agent" where the
video says `catalog_agent`; "save customer details" under the order agent).

**The opening failed.** It began "In the last video, we built…" (context new
viewers don't have), promised and showed no payoff, went back to "What is an
agent?" at 0:27 (losing the advanced audience the title attracted), and put the
strongest material (the overloaded-agent problem and the live customer demo)
after ~2.5 minutes of theory.

**Rules added:** hook-first opening (pain → 5s result preview → promise + repo
link in 30s), no previous-video reference up front, depth matches the title,
demo in the first third, short CTA, chapter list; thumbnails with ≤3 words, one
idea, large face, one small logo, labels that match, 2–3 variants; three titles
with the hook in ~45 characters and no leading series name; 2–3 Shorts per
long video. See `../SKILL.md` and `../../make-a-video/references/script-roadmap-intro.md`.
