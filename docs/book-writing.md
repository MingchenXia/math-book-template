# Writing a mathematical book

Use the plan's intended reader and scope to decide what to explain,
prove or import. Use the blueprint to check the order in which the
reader meets definitions and results. Keep decisions about this
particular book, including prerequisites, citation placement and
typography, in the project files. [Plan](../PLAN.md) ·
[Blueprint](../BLUEPRINT.md)

## Give the reader a route through the mathematics

- The preface states the readership, prerequisites and possible reading
  routes. The introduction gives the central question and main results
  early. Explain what changes from the established setting when that
  comparison helps the reader understand the proof. A worked example
  can introduce a construction that recurs later.
- Open a part by explaining how its chapters depend on one another.
  Open a chapter or section with the mathematical question, example
  or obstruction that makes its next construction necessary. Point to
  the principal result and explain the connection. Keep a short
  opening when it already does that work.
- Use headings that name the mathematical object, question or
  argument. Trim repeated roadmaps and paragraphs that merely list
  results in order of appearance.
- Give each definition and reusable result one natural home before
  its first use. Refer back to it from later chapters. Introduce
  specialized background near the argument that needs it.

## State the setting at the point of use

- Read in the reader's order, including introductions and examples.
  Introduce spaces, symbols and conventions before the first formula
  that uses them. Declare global sign and normalization conventions
  once. Carry standing hypotheses through a section and state changes
  of setting where they occur.
- Put local assumptions on the assertions that need them. For example,
  boundedness of a continuous real-valued function on a compact space
  allows an empty space, while attainment of extrema needs
  nonemptiness. Retain the actual hypothesis when removing repeated
  qualifications or moving results between chapters.
- State the norm or topology in a completeness or convergence claim
  and the parameters in a uniform estimate. Identify the action or
  invariance used in a symmetry reduction. Distinguish existence,
  uniqueness of a solution and convergence to a selected solution.
- Choose semantic theorem environments and stable labels. Use
  `\eqref` for equation references and the project's cross-reference
  conventions for other results. Keep notation and layout consistent
  with the existing class and preamble.

## Explain proofs and credit sources

- Expose the step that makes the argument work. Give the reason for
  each nontrivial implication where it is used, including the
  exceptional cases, limit passages and dependence of constants.
  Use displays for formulas a reader needs to examine. Give worked
  examples enough calculation to support their conclusions.
- Before rewriting a result, compare its hypotheses, conclusion and
  dependencies with the original. After incorporating a new result,
  check introductions, later uses, examples and open questions for
  superseded claims. Keep any unresolved scope explicit.
- Credit the actual authors and distinguish an original contribution
  from a later extension or an independent proof in the book. Check
  the cited version, exact theorem, section or page, and the
  hypotheses of the imported result. Use a single bibliography.
  When the book places attribution in source notes, link those notes
  to the precise results they document. Apply any special citation
  or source-retention instructions to the material they govern.

## Finish a chapter in the compiled book

1. Read the original unit and locate all active nested inputs, figures
   and incorporated proofs. For a complete chapter revision, read
   the whole chapter, its dependencies and the transitions to the
   neighboring chapters. For a local correction, follow the affected
   statements and uses through the book.
2. Read the finished unit twice. In the first pass trace each statement
   through its proof and sources. In the second pass read continuously
   from statements through proofs, checking first-use definitions,
   shifted assumptions and continuity of exposition. Recheck the
   affected passages after further edits.
3. Build and inspect the final PDF. Follow the contents, outline and
   cross-references. Check theorem statements, display lead-ins,
   figures and captions, and proof endings across page breaks.
   Inspect the neighboring pages after a pagination change. Record
   the physical PDF page range for an excerpt and use the printed
   page labels when discussing the book's pagination.
4. Maintain the generated subject index as the book grows. Index terms
   at their definitions, principal results or useful examples. Use
   subentries or cross-references for related terms, and inspect page
   locators and wrapping in the PDF. Let the index paginate naturally.
5. Hand the exact source and PDF scope to the independent reviewer.
   Record proof reconstruction, checked source locators, compilation
   and visual inspection separately, with remaining issues and the
   next unit in the project status. Follow the existing
   [review workflow](workflow.md).

When author feedback reveals a recurring problem, update the relevant
guidance once and check how it applies in a neighboring case. Record a
local preference with its scope in the book's plan. Keep editorial
records in the repository's working documents.
