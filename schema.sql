 -- WARNING: This schema is for context only and is not meant to be run.
 -- Table order and constraints may not be valid for execution.

 CREATE TABLE public.shops (
   id uuid NOT NULL DEFAULT auth.uid(),
   created_at timestamp with time zone NOT NULL DEFAULT now(),
   name text NOT NULL,
   address text NOT NULL,
   telefon text,
   email text NOT NULL,
   website text,
   activity_type ARRAY NOT NULL,
   picture text,
   CONSTRAINT shops_pkey PRIMARY KEY (id)
 );
 CREATE TABLE public.users (
   id uuid NOT NULL DEFAULT auth.uid(),
   created_at timestamp with time zone NOT NULL DEFAULT now(),
   first_name text NOT NULL,
   last_name text NOT NULL,
   email text NOT NULL,
   age integer,
   interests ARRAY NOT NULL,
   number_children integer,
   CONSTRAINT users_pkey PRIMARY KEY (id)
 );
 CREATE TABLE public.children (
   id uuid NOT NULL DEFAULT gen_random_uuid(),
   created_at timestamp with time zone NOT NULL DEFAULT now(),
   user_id uuid NOT NULL DEFAULT gen_random_uuid(),
   first_name text NOT NULL,
   last_name text,
   age integer NOT NULL,
   interests ARRAY NOT NULL,
   gender text,
   CONSTRAINT children_pkey PRIMARY KEY (id),
   CONSTRAINT Children_User_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
 );
 CREATE TABLE public.activities (
   id uuid NOT NULL DEFAULT gen_random_uuid(),
   created_at timestamp with time zone NOT NULL DEFAULT now(),
   shop_id uuid NOT NULL DEFAULT gen_random_uuid(),
   title text NOT NULL,
   description text,
   price real,
   participants_max integer NOT NULL,
   duration text NOT NULL,
   age_group text,
   picture text NOT NULL,
   CONSTRAINT activities_pkey PRIMARY KEY (id),
   CONSTRAINT Activities_Shop_ID_fkey FOREIGN KEY (shop_id) REFERENCES public.shops(id)
 );
 CREATE TABLE public.bookings (
   id uuid NOT NULL DEFAULT gen_random_uuid(),
   created_at timestamp with time zone NOT NULL DEFAULT now(),
   user_ID uuid NOT NULL DEFAULT gen_random_uuid(),
   shop_ID uuid NOT NULL DEFAULT gen_random_uuid(),
   slot text NOT NULL,
   quantity integer,
   total_price real,
   status text NOT NULL,
   CONSTRAINT bookings_pkey PRIMARY KEY (id),
   CONSTRAINT Bookings_User_ID_fkey FOREIGN KEY (user_ID) REFERENCES public.users(id),
   CONSTRAINT Bookings_Shop_ID_fkey FOREIGN KEY (shop_ID) REFERENCES public.shops(id)
 );
