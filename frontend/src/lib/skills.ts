/** Client-side skill lexicon used only by the product prototype.

This list is intentionally small and matches the Python extraction helper.
It is not a trained NER model and must not be presented as matching accuracy.
*/

export const SKILL_LEXICON: Record<string, string[]> = {
  python: ["python"],
  java: ["java"],
  javascript: ["javascript", "js"],
  sql: ["sql"],
  pandas: ["pandas"],
  numpy: ["numpy"],
  "scikit-learn": ["scikit-learn", "sklearn"],
  tensorflow: ["tensorflow"],
  react: ["react"],
  docker: ["docker"],
  aws: ["aws", "amazon web services"],
  git: ["git"],
  html: ["html"],
  css: ["css"],
  linux: ["linux"],
};

export function extractSkillNames(text: string): string[] {
  const haystack = text.toLowerCase();
  const found: string[] = [];
  for (const [canonical, surfaces] of Object.entries(SKILL_LEXICON)) {
    const hit = surfaces.some((surface) => {
      if (/^[a-z0-9]+$/.test(surface)) {
        const pattern = new RegExp(`\\b${surface}\\b`, "i");
        return pattern.test(haystack);
      }
      return haystack.includes(surface);
    });
    if (hit) found.push(canonical);
  }
  return found;
}

export function overlapSkills(resumeText: string, jobText: string) {
  const resume = extractSkillNames(resumeText);
  const job = extractSkillNames(jobText);
  const resumeSet = new Set(resume);
  const jobSet = new Set(job);
  return {
    shared: job.filter((name) => resumeSet.has(name)),
    resumeOnly: resume.filter((name) => !jobSet.has(name)),
    jobOnly: job.filter((name) => !resumeSet.has(name)),
  };
}
