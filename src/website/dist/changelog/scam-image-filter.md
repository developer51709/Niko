# Scam Image Filter (Experimental)

- Date: 2026-10-01
- Tags: automod, scam, images, experimental, dashboard, discord

A community-driven image filter that catches known MrBeast scam images: members report suspicious messages, Niko staff verify them, and confirmed images are then detected and removed automatically — with a feedback loop that lets servers flag false positives to improve accuracy. The feature is still in early testing and may have some reliability issues.

## Highlights

### One-Click Reporting
Anyone can right-click a suspicious message and choose “Report MrBeast Scam”. The message's image assets, author, server, and a jump link are forwarded to the scam review queue in Niko's private staff server.

### Perceptual Hash Detection
Confirmed images are fingerprinted with a 64-bit difference hash and compared by visual similarity, so resized, re-compressed, and re-encoded copies of a known scam image are still caught — even when the file itself is different.

### Staff-Verified Review Queue
Nothing enters the filter automatically. Niko staff review each report and press Confirm Scam (or Reject). Multi-image reports store a fingerprint for every image, and confirmations work offline because hashes are captured at report time.

### False-Positive Feedback Loop
Every removal is logged to the server's automod log channel with the original images and a “Report False Positive” button. Reports land back in the staff queue where a “Remove From Filter” action deletes the hash, steadily improving accuracy.

## Changes

### added
- “🚩 Report MrBeast Scam” message context-menu command that forwards image assets and context to the staff-only review channel
- Persistent Confirm Scam / Reject buttons on review reports that survive bot restarts, restricted to Niko staff
- Perceptual image fingerprinting (64-bit dHash with Hamming-distance matching) so re-encoded and resized scam variants are detected
- Automatic deletion of messages matching confirmed scam hashes in servers that enable the filter, with per-hash deletion counters
- Automod log channel entry for every removal, including the original image gallery and a Report False Positive button
- False-positive review cards with a Remove From Filter action so mis-detections can be pulled from the database
- Per-guild Scam Images toggle in the /automod command panel (all languages) and the dashboard's AutoMod modules
- Experimental badge and early-testing warning on both the command panel and the dashboard
- Dedicated database tables for confirmed scam hashes and report history, with counter tracking for deletions and false positives

### improved
- Application-command error routing so every slash and context-menu failure now replies to the user instead of failing silently
- Automod log delivery works identically on both SQLite and MongoDB deployments
- Attachments no longer wake the AI on their own — images and voice only add context when Niko is triggered by name, ping, or command
