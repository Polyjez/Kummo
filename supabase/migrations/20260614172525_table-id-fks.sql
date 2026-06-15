ALTER TABLE public.bookings ALTER COLUMN user_id DROP DEFAULT;
ALTER TABLE public.bookings ALTER COLUMN shop_id DROP DEFAULT;

ALTER TABLE public.children ALTER COLUMN user_id DROP DEFAULT;

ALTER TABLE public.activities ALTER COLUMN shop_id DROP DEFAULT;
