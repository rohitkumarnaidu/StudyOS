-- StudyOS — Phase 6: Achievements and user achievements for gamification.

CREATE TABLE IF NOT EXISTS public.achievements (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text NOT NULL UNIQUE,
  title text NOT NULL,
  description text NOT NULL,
  icon text NOT NULL DEFAULT 'trophy',
  category text NOT NULL DEFAULT 'general' CHECK (category IN ('streak', 'progress', 'quiz', 'milestone', 'special')),
  requirement int NOT NULL DEFAULT 1,
  requirement_type text NOT NULL DEFAULT 'count' CHECK (requirement_type IN ('count', 'days', 'score', 'percent')),
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.achievements IS 'Achievement definitions (system-wide, not user-specific).';

CREATE TABLE IF NOT EXISTS public.user_achievements (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  achievement_id uuid NOT NULL REFERENCES public.achievements(id) ON DELETE CASCADE,
  unlocked_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.user_achievements IS 'User-unlocked achievements.';

CREATE UNIQUE INDEX IF NOT EXISTS user_achievements_unique_uidx ON public.user_achievements(profile_id, achievement_id);

CREATE INDEX IF NOT EXISTS user_achievements_profile_idx ON public.user_achievements(profile_id, unlocked_at DESC);

-- RLS
ALTER TABLE public.achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_achievements ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public can read achievements" ON public.achievements;
CREATE POLICY "Public can read achievements" ON public.achievements
  FOR SELECT USING (is_active = true);

DROP POLICY IF EXISTS "Users can view own achievements" ON public.user_achievements;
CREATE POLICY "Users can view own achievements" ON public.user_achievements
  FOR SELECT USING (auth.uid() = profile_id);

-- Seed common achievements
INSERT INTO public.achievements (code, title, description, icon, category, requirement, requirement_type) VALUES
('streak_3', 'Getting Started', 'Maintain a 3-day study streak', 'flame', 'streak', 3, 'days'),
('streak_7', 'Week Warrior', 'Maintain a 7-day study streak', 'flame', 'streak', 7, 'days'),
('streak_30', 'Monthly Master', 'Maintain a 30-day study streak', 'flame', 'streak', 30, 'days'),
('streak_100', 'Century Club', 'Maintain a 100-day study streak', 'crown', 'streak', 100, 'days'),
('chapter_10', 'Explorer', 'Complete 10 chapters', 'compass', 'progress', 10, 'count'),
('chapter_50', 'Scholar', 'Complete 50 chapters', 'book-open', 'progress', 50, 'count'),
('chapter_91', 'NEET Master', 'Complete all 91 chapters', 'graduation-cap', 'progress', 91, 'count'),
('quiz_10', 'Quiz Taker', 'Complete 10 quizzes', 'target', 'quiz', 10, 'count'),
('quiz_perfect', 'Perfect Score', 'Score 100% on any quiz', 'star', 'quiz', 100, 'percent'),
('subtopic_100', 'Centurion', 'Complete 100 subtopics', 'check-circle', 'milestone', 100, 'count'),
('subtopic_500', 'Overachiever', 'Complete 500 subtopics', 'trophy', 'milestone', 500, 'count'),
('first_login', 'Welcome!', 'Complete your first study session', 'sparkles', 'special', 1, 'count');
