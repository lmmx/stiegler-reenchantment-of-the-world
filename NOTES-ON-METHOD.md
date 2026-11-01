# Notes on method

[README](README.md) › **Method**

This file records how the companion was built: what was read, what was not, how claims are sourced, the fair-use stance, and what remains open. Read it before relying on any L3 detail.

## 1. Aims and constraints

- **Objective account.** The repo reports what the book argues, kept apart from evaluation. Evaluation lives in [reception.md](reception.md) and [sources/EVALUATION.md](sources/EVALUATION.md). Interpretive remarks elsewhere are prefixed **"Labelled interpretation"**.
- **Progressive disclosure.** [README](README.md) (L0) → [overview.md](overview.md) (L1) → `chapters/` (L2 abstracts and claims) → L3 section tables inside each chapter file. Each layer links down to the next. Cross-cutting [concepts/](concepts/) and [GLOSSARY.md](GLOSSARY.md) sit alongside, and [INDEX.md](INDEX.md) maps across all three.
- **Markdown only, no code.**
- **Fair use.** The repo is private and for personal study. It contains **no continuous text of the book**. Summaries are our paraphrase. Direct quotations are short (generally under 40 words), attributed and page-referenced, and used only where wording matters. Third-party sources are stored as condensed accounts with short attributed quotations, never as full copies. Where a source is openly licensed (e.g. the Lotz review, CC BY-NC-ND), we still condense rather than reproduce.

## 2. What original text was consulted (not stored)

| Text | Access | Used for |
|---|---|---|
| Bloomsbury publisher preview (14 pp.: front matter, contents, Translator's Preface, Introduction pp. 1–3) | pageplace.de preview PDF | Structure, pagination, Preface, Introduction opening |
| Ars Industrialis **2005 Manifesto** (EN web version + FR) | arsindustrialis.org | Full 2005 Manifesto file |
| Ars Industrialis **2010 Manifesto** (EN web version + FR) | arsindustrialis.org | Full 2010 Manifesto file |
| **Tunis motion** (FR, *Libération* 14 Nov 2005) | arsindustrialis.org | Motion file |
| Stiegler, **talk of 24 Sept 2005** (Théâtre de la Colline) | arsindustrialis.org | **Chapter 2** (precursor; its headings match the chapter's) |
| French edition, **back cover, dedication, Ch. 1 §3 (pp. 42–47)** | third-party transcription (homocoques.com) | Ch. 1 §3; FR paratext |
| Perlego listing (contents; preview fragment of p. 93) | perlego.com | Cross-check of contents; ending of Ch. 2 / motion |
| **The owner's own copy of the English edition**: 66 photographs of pp. 1–9, 11–15, 17–60 and Notes pp. 101–108 (blank pp. 10 and 16 not photographed) | Supplied by the repo owner (Nov 2026); processed outside the repo (see below) | **Introduction pp. 4–9, both manifestos (exact pages), all of Chapter 1, notes to Introduction, manifestos and Ch. 1** |

**Not consulted:** the printed English Chapter 2 (pp. 61–94), the printed Tunis motion (pp. 95–100), the Chapter 2 and motion notes (pp. 108–112) and the Bibliography. The French edition as a whole was not consulted either. No full text was obtained from shadow libraries. Pirate copies surfaced in search results and were deliberately not opened. Automated access to Google Books was blocked, and we did not try to get around that.

The web versions of the manifestos are the association's own translations, not Trevor Arthur's. The manifesto files now take their page numbers and wording checks from the printed text.

**How the photographs were processed** (outside the repo; neither the images nor the OCR text are stored in the repo):
1. **Orientation.** Each photo was OCR'd at three rotations and the best-scoring one kept (51 turned counter-clockwise, 2 clockwise, 13 upright).
2. **Dewarping.** [page-dewarp](https://github.com/lmmx/page-dewarp) 0.3.4 with the JAX batch backend (parallel L-BFGS on CPU, about 48 s for 66 images), writing a JSON parameter sidecar for each page. 64/66 pages dewarped. Two (book pp. 47 and 53) failed with an implausible memory allocation, which looks like a degenerate page-size fit and may be worth reporting upstream. Optimisation improvements ranged from 13% to over 80%.
3. **OCR.** RapidOCR (PP-OCRv6, ONNX Runtime, CPU) on both the dewarped and the upright image, keeping the better result per page. Lines were then put in layout order (sorted by position, with upside-down pages detected from headers) and fragments of the facing page were filtered out.
4. **Quality.** Mean OCR confidence was 0.90–0.99 per page. One page (p. 22) stayed below 0.90 after a rerun on the raw photo. Some 25 strongly skewed or curved pages yielded incomplete OCR (missed lines), and those pages were read from the photographs as a last resort. A per-page log (photo → page, dewarp objective before and after, OCR source, confidence, word count, flags) is kept in the session scratchpad.

## 3. How sources were found

1. **Bibliographic verification first.** We searched publisher and retailer records (Bloomsbury, Perlego, Google Books listing, Flammarion, BnF/library catalogues), then downloaded the publisher preview to fix the contents.
2. **Primary-adjacent sweep of arsindustrialis.org.** We read the manifesto pages, the "textes" index and the Tunis materials. This turned up the 2005 Colline talk, whose section headings reproduce Chapter 2's. Finding it was the single biggest gain in coverage.
3. **Parallel research in three strands**, each saving condensed source files under `sources/`:
   - **Reviews of the book** (`review-*`): English, French, Afrikaans/South African, catalogue and publisher material.
   - **Secondary literature and glossaries on the concepts** (`lit-*`, `glossary-*`, `primary-parallel-*`): Ross, Lemmens, Hui, Abbinnett, Alombert, the Ars Industrialis *Vocabulaire*, and others.
   - **Media, practitioner and context sources** (`media-*`, `context-*`): podcasts, lectures, blogs, wikis; Medef 2005, Le Lay 2004, WSIS 2005.
4. **Search techniques:** English and French queries; exact section titles in both languages; names of reviewers; venue-specific searches (Marx & Philosophy, Critical Inquiry, Radical Philosophy, Parrhesia, TCS, NDPR, Cairn, OpenEdition); and following citations inside retrieved sources.
5. **Every source file** carries front-matter (title, author, venue, date, URL, accessed, language, type) and three sections: *Condensed account*, *Short quotations*, *Notes for evaluation*.

## 4. Confidence conventions

- **high**: read in the primary text (or in a primary text demonstrably identical in argument).
- **medium**: reconstructed from a precursor text plus page-cited secondary claims.
- **low**: section title plus parallel works only. Content is flagged as probable, not attested.

Page numbers are to the **English edition (Bloomsbury 2014)** unless marked "FR". "(Lotz)" and similar markers mean the page reference is that reviewer's.

## 5. Gaps and open questions

1. ~~Chapter 1 body text~~ **Resolved** with the owner's copy: "R technologies" are relational technologies (p. 29); "the plane that enchants me" is the plane of consistencies or motifs (pp. 58–60), and the earlier mistranslation flag is withdrawn; the *sursaut* is the re-founding of the "human enterprise" (*entreprendre de fonder*, p. 46), with no mention of the Camdessus report.
2. **Chapter 2 additions.** The book version extends the 2005 talk (Wikipedia, judgement, collective intelligence). The extent of the revision is unknown.
3. ~~Introduction pp. 4–10~~ **Resolved** (pp. 4–9 read; p. 10 blank). The Introduction also states the book's provenance (p. 8) and that the motion is printed complete (p. 9).
4. **The French table of contents** has not been seen complete. We do not know whether the French edition titles the Introduction "Que faire ?", whether it prints the Tunis motion, or where its chapter breaks fall.
5. **Dedication** (Simon Nora; Laurence Parisot): attested for the French edition by one transcription. Whether it is in the English edition is still unknown, since the front matter was not photographed. Simon Nora is in any case cited in Ch. 1 (p. 48, n. 37).
6. **Authorship.** The Introduction (p. 8) says the two chapters rework papers "that I presented". They are Stiegler's own, written in the first person ("I founded", p. 6). The manifestos are signed by the five founders.
7. **Translation quality** has not been assessed against the French. The "plan/plane" question is resolved in the translation's favour. Visible slips in the English include "Georges Collis" for Collins (p. 8), "DESUMBLIMATION" (p. 39) and "Toubiana" for Tubiana.
8. **Secondary sources searched for but not obtained:** Crogan (*Cultural Politics* 2010), Gerald Moore and *Stiegler and Technics* (2013), Daniel Ross's "Ecology of Spirit", the *Spirale* review (2007), Alombert/CosTECH, any *Parrhesia* or NDPR item on this book. There is no podcast devoted to the book; one Stiegler interview podcast (MACBA 2019) was found, known from its description only. The full list is in [sources/EVALUATION.md](sources/EVALUATION.md) §F.
9. **Lawful full-text routes exhausted (1 Nov 2026):**
   - Publisher preview: only pp. v–3 available.
   - Google Books: automated access blocked.
   - Flammarion site: request rejected.
   - Decitre, Ombres Blanches, Eyrolles, Furet: 403 or 503.
   - Open Library: two French works, `no_ebook`; English edition not found.
   - Internet Archive: no copy.
   - HathiTrust: no record for ISBN 9781441169259.
   - Barker, *New Formations* 77: paywalled; only the issue editorial was readable.

   Shadow-library copies were found in search results and deliberately not opened. The gap was then closed with the owner's own copy (see §2).
10. **Audio and video** (Ars Industrialis session recordings, interviews) were not listened to. Only pages, minutes and transcripts were read.

## 6. How to extend this repo

- Remaining work with the printed book: Chapter 2 (pp. 61–94) against its 2005 precursor, and the complete Tunis motion (pp. 95–100). Use the same pipeline: photograph, dewarp, OCR, then summarize.
- Add new sources as `sources/<type>-<author>-<slug>-<year>.md` with the same front-matter, then add a row in [sources/EVALUATION.md](sources/EVALUATION.md) and links in [INDEX.md](INDEX.md).
- Keep your own reading in a separate file or folder (e.g. `notes/`) so the objective layers stay clean.
