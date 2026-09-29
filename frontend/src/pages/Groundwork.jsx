import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import { api } from "@/lib/api";

const EASE = [0.22, 1, 0.36, 1];

const Section = ({ label, children, testId, delay = 0 }) => (
  <motion.section
    data-testid={testId}
    initial={{ opacity: 0, y: 14 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.8, ease: EASE, delay }}
    className="border-t border-[#E2DFD8] pt-10 mt-16 first:border-t-0 first:pt-0 first:mt-0"
  >
    <span className="text-xs tracking-[0.18em] uppercase text-[#8A8F8C]">{label}</span>
    <div className="mt-4">{children}</div>
  </motion.section>
);

const OpenLink = ({ to, testId, children }) => (
  <Link
    to={to}
    data-testid={testId}
    className="group inline-flex items-center gap-1.5 text-[15px] text-[#5C605A] hover:text-[#2C2D2B] transition-colors mt-6"
  >
    <span className="border-b border-transparent group-hover:border-[#9DB0A3] transition-colors pb-0.5">
      {children}
    </span>
    <ArrowUpRight size={16} strokeWidth={1.5} className="text-[#9DB0A3]" />
  </Link>
);

const TIER_ORDER = ["dream", "target", "safe"];

export default function Groundwork() {
  const location = useLocation();
  const [dream, setDream] = useState(null);
  const [nudge, setNudge] = useState(null);
  const [countdown, setCountdown] = useState(null);
  const [coverage, setCoverage] = useState(null);
  const [storyCount, setStoryCount] = useState(null);
  const [circle, setCircle] = useState([]);
  const [othersCount, setOthersCount] = useState(0);
  const [ready, setReady] = useState(false);

  // Fast, local DB reads — render the hub as soon as these resolve. We refetch
  // whenever we land on /groundwork so the prep-circle lens always reflects the
  // single people collection (one source of truth).
  useEffect(() => {
    let alive = true;
    setReady(false);
    (async () => {
      const [d, cov, st, ppl] = await Promise.all([
        api.dreamOverview().catch(() => ({ companies: [] })),
        api.storyCoverage().catch(() => null),
        api.stories().catch(() => ({ stories: [] })),
        api.people().catch(() => ({ people: [] })),
      ]);
      if (!alive) return;
      setDream(d?.companies || []);
      setCoverage(cov);
      setStoryCount((st?.stories || []).length);
      const people = ppl?.people || [];
      setCircle(people.filter((p) => p.prep_group === true));
      setOthersCount(people.filter((p) => p.prep_group !== true).length);
      setReady(true);
    })();
    return () => {
      alive = false;
    };
  }, [location.pathname]);

  // Optional extras (nudge may hit the LLM and be slow) — fetched separately so
  // they never block the hub from rendering; shown only once/if they arrive.
  useEffect(() => {
    let alive = true;
    api.dreamNudges().then((n) => alive && setNudge(n?.nudge || null)).catch(() => {});
    api.countdown().then((c) => alive && setCountdown(c?.countdown || null)).catch(() => {});
    return () => {
      alive = false;
    };
  }, [location.pathname]);

  // --- Dream Offer summary ---
  const tierCounts = (dream || []).reduce((acc, c) => {
    acc[c.tier] = (acc[c.tier] || 0) + 1;
    return acc;
  }, {});
  const dreamNames = (dream || []).filter((c) => c.tier === "dream").map((c) => c.name);
  const totalCompanies = (dream || []).length;
  const pipelineLine = totalCompanies
    ? TIER_ORDER.filter((t) => tierCounts[t]).map((t) => `${tierCounts[t]} ${t}`).join(" · ")
    : null;

  // --- Stories summary ---
  const covered = coverage
    ? coverage.competencies.filter((c) => (coverage.counts[c] || 0) > 0).length
    : 0;
  const totalComp = coverage ? coverage.competencies.length : 8;

  return (
    <div data-testid="groundwork-page">
      <span className="text-xs tracking-[0.18em] uppercase text-[#8A8F8C]">Groundwork</span>
      <h1 className="font-editorial text-5xl md:text-6xl text-[#2C2D2B] mt-2 mb-6">
        Your placement ground
      </h1>
      <p className="font-editorial text-xl md:text-2xl italic leading-relaxed text-[#5C605A] max-w-xl">
        Everything for the offer lives here — the companies you’re reaching for, the stories
        you’ll tell, and the people preparing alongside you. No rush. Just the next honest step.
      </p>

      <div className="mt-16">
        {/* DREAM OFFER */}
        <Section label="Dream Offer" testId="groundwork-dream-section">
          <h2 className="font-editorial text-3xl md:text-4xl text-[#2C2D2B]">
            The companies you’re reaching for
          </h2>
          {ready && (
            <div className="mt-4 space-y-2">
              {totalCompanies ? (
                <>
                  {dreamNames.length > 0 && (
                    <p className="text-[#2C2D2B] text-[17px]">{dreamNames.join(" · ")}</p>
                  )}
                  <p className="text-[#8A8F8C] text-[15px]">
                    {totalCompanies} in your pipeline{pipelineLine ? ` — ${pipelineLine}` : ""}.
                  </p>
                </>
              ) : (
                <p className="text-[#8A8F8C] text-[15px]">
                  No companies yet — a calm place to name the ones you’re reaching for.
                </p>
              )}
              {nudge && (
                <p className="text-[#5C605A] text-[15px] italic pt-2">
                  {typeof nudge === "string" ? nudge : nudge.text || nudge.message}
                </p>
              )}
              {countdown && countdown.days_left != null && (
                <p className="text-[#5C605A] text-[15px] pt-1">
                  {countdown.days_left} days to {countdown.target || "the next round"}.
                </p>
              )}
            </div>
          )}
          <OpenLink to="/dream-offer" testId="groundwork-open-dream">
            Open Dream Offer
          </OpenLink>
        </Section>

        {/* STORIES */}
        <Section label="Stories" testId="groundwork-stories-section" delay={0.05}>
          <h2 className="font-editorial text-3xl md:text-4xl text-[#2C2D2B]">
            The stories you’ll tell
          </h2>
          {ready && (
            <p className="mt-4 text-[#8A8F8C] text-[15px]">
              {storyCount
                ? `${storyCount} ${storyCount === 1 ? "story" : "stories"} shaped · covering ${covered} of ${totalComp} competencies.`
                : "Your story bank is empty — a good place to begin shaping one."}
            </p>
          )}
          <OpenLink to="/stories" testId="groundwork-open-stories">
            Open Story Bank
          </OpenLink>
        </Section>

        {/* PREP CIRCLE */}
        <Section label="Your Prep Circle" testId="groundwork-prep-circle-section" delay={0.1}>
          <h2 className="font-editorial text-3xl md:text-4xl text-[#2C2D2B]">
            The people preparing with you
          </h2>
          {ready && (
            <div className="mt-6">
              {circle.length ? (
                <div className="space-y-6">
                  {circle.map((p) => (
                    <div key={p.id} data-testid={`groundwork-circle-person-${p.id}`}>
                      <div className="flex items-baseline gap-3">
                        <span className="text-[17px] text-[#2C2D2B]">{p.name}</span>
                        {p.relation && (
                          <span className="text-xs text-[#8A8F8C]">{p.relation}</span>
                        )}
                      </div>
                      {p.strengths?.length > 0 ? (
                        <div className="flex flex-wrap gap-2 mt-2">
                          {p.strengths.map((s) => (
                            <span
                              key={s}
                              className="text-xs text-[#5C605A] bg-[#EFECE7] rounded-full px-3 py-1"
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-[#8A8F8C] mt-1 italic">
                          Strengths not noted yet.
                        </p>
                      )}
                      {p.strength_note && (
                        <p className="text-sm text-[#8A8F8C] mt-2 italic">{p.strength_note}</p>
                      )}
                    </div>
                  ))}
                  <p className="text-[15px] text-[#8A8F8C] pt-1">
                    Log or revisit mock interviews with anyone in your circle over in People.
                  </p>
                </div>
              ) : (
                <p className="text-[#8A8F8C] text-[15px]">
                  No one in your prep circle yet — you can bring peers in from People whenever
                  you’re ready.
                </p>
              )}
            </div>
          )}
          <OpenLink to="/people" testId="groundwork-open-people">
            Open People
          </OpenLink>
        </Section>
      </div>
    </div>
  );
}
