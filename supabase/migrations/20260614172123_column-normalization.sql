-- Rename columns to lowercase
ALTER TABLE public.bookings RENAME COLUMN "user_ID" TO user_id;
ALTER TABLE public.bookings RENAME COLUMN "shop_ID" TO shop_id;

-- Rename the foreign key constraints to match the new convention
ALTER TABLE public.bookings RENAME CONSTRAINT "Bookings_User_ID_fkey" TO bookings_user_id_fkey;
ALTER TABLE public.bookings RENAME CONSTRAINT "Bookings_Shop_ID_fkey" TO bookings_shop_id_fkey;
