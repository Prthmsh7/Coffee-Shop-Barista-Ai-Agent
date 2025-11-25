import { Button } from '@/components/livekit/button';

const COFFEE_SHOP_NAME = 'Ember & Oak Coffeehouse';
const BARISTA_NAME = 'Ember';

function WelcomeImage() {
  return (
    <svg
      width="120"
      height="120"
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="mb-6 h-28 w-28 text-primary/80"
    >
      <rect x="15" y="55" width="70" height="32" rx="12" fill="currentColor" opacity="0.2" />
      <path
        d="M26 42h58c3.314 0 6 2.686 6 6v18c0 10.494-8.506 19-19 19H39c-10.494 0-19-8.506-19-19V48c0-3.314 2.686-6 6-6Z"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M90 52h9c5.523 0 10 4.477 10 10s-4.477 10-10 10h-6"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M44 28c0 6-4 8-4 12s4 4 4 8M60 28c0 6-4 8-4 12s4 4 4 8M76 28c0 6-4 8-4 12s4 4 4 8"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref}>
      <section className="flex flex-col items-center justify-center rounded-3xl border border-border/60 bg-gradient-to-b from-[#fff4e3] via-[#f1d3ac] to-[#e4b17f] px-8 py-12 text-center shadow-[0_25px_65px_rgba(43,22,12,0.25)]">
        <WelcomeImage />
        <p className="text-xs uppercase tracking-[0.5em] text-[#3d1f11]/80">{COFFEE_SHOP_NAME}</p>
        <h1
          className="mt-4 text-3xl font-semibold text-[#2b160c] sm:text-4xl"
          style={{ fontFamily: 'var(--font-playfair, var(--font-public-sans))' }}
        >
          Meet {BARISTA_NAME}, your vintage-inspired barista
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-base leading-7 text-[#4a2d20]">
          Order single-origin pours, tweak milk, add your favorite drizzle, and get a tidy written
          summary of the order before you hear it called out. Ember keeps the vibe cozy while making
          sure nothing gets lost in the grind.
        </p>

        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="mt-8 w-64 rounded-full font-semibold shadow-[0_15px_35px_rgba(140,75,43,0.35)]"
        >
          {startButtonText}
        </Button>
      </section>

    </div>
  );
};
