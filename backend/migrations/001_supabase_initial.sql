-- ============================================================
-- TitanCare EV — Supabase Migration 001
-- Denormalized & type-safe schema
-- ============================================================

-- Enable UUID extension (already on in Supabase by default)
create extension if not exists "uuid-ossp";

-- ============================================================
-- CARS
-- ============================================================
create table public.cars (
  id                          uuid primary key default uuid_generate_v4(),

  -- Identity
  model                       text not null,
  sub_model                   text,

  -- Pricing
  starting_price              numeric(12, 2),

  -- Dimensions (split from "4270 x 1850 x 1575")
  length_mm                   integer,
  width_mm                    integer,
  height_mm                   integer,
  wheelbase_mm                integer,

  -- Cabin
  seating_capacity            smallint,
  trunk_volume_min_l          integer,
  trunk_volume_max_l          integer,   -- NULL when single value
  curb_weight_min_kg          integer,
  curb_weight_max_kg          integer,   -- NULL when single value

  -- Battery
  battery_type                text,
  battery_capacity_kwh        numeric(6, 2),

  -- Range (split from "400 (NEDC)")
  range_km                    integer,
  range_standard              text check (range_standard in ('NEDC', 'WLTP', 'EPA')),

  -- Charging
  ac_charging_kw              numeric(5, 1),
  dc_charging_kw              numeric(5, 1),
  max_dc_fast_charging_kw     numeric(5, 1),
  dc_fast_charging_30_80_min  integer,   -- extracted numeric from "24 min"

  -- V2L
  v2l                         boolean default false,

  -- Performance
  max_power_kw                numeric(6, 1),
  max_torque_nm               numeric(7, 1),
  acceleration_0_100_s        numeric(4, 1),

  -- Drive
  drive_type                  text,      -- e.g. "FWD", "RWD", "AWD"
  drive_modes                 text[],    -- e.g. ARRAY['ECO', 'NORMAL', 'SPORT']

  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

alter table public.cars enable row level security;

create policy "Public read cars"
  on public.cars for select using (true);

create index cars_model_idx      on public.cars (model);
create index cars_sub_model_idx  on public.cars (sub_model);
create index cars_price_idx      on public.cars (starting_price);


-- ============================================================
-- APPOINTMENTS
-- ============================================================
create table public.appointments (
  id                uuid primary key default uuid_generate_v4(),

  -- Customer
  customer_name     text not null,
  customer_email    text not null,
  customer_phone    text not null,

  -- Vehicle — soft reference by model name; use car_id when possible
  car_id            uuid references public.cars (id) on delete set null,
  vehicle_model     text,   -- kept for backward-compat / free-text fallback

  -- Service
  service_type      text not null,
  appointment_date  date not null,
  appointment_time  time not null,
  notes             text,
  status            text not null default 'Scheduled'
                    check (status in ('Scheduled', 'Confirmed', 'Completed', 'Cancelled')),

  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

alter table public.appointments enable row level security;

-- Staff can see all; customers can only see their own (extend as needed)
create policy "Staff read appointments"
  on public.appointments for select using (true);

create index appointments_date_idx    on public.appointments (appointment_date);
create index appointments_status_idx  on public.appointments (status);
create index appointments_email_idx   on public.appointments (customer_email);


-- ============================================================
-- AUTO-UPDATE updated_at
-- ============================================================
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger cars_updated_at
  before update on public.cars
  for each row execute function public.set_updated_at();

create trigger appointments_updated_at
  before update on public.appointments
  for each row execute function public.set_updated_at();


-- ============================================================
-- SEED: Cars data (denormalized from SQLite)
-- ============================================================
insert into public.cars (
  model, sub_model, starting_price,
  length_mm, width_mm, height_mm, wheelbase_mm,
  seating_capacity,
  trunk_volume_min_l, trunk_volume_max_l,
  curb_weight_min_kg, curb_weight_max_kg,
  battery_type, battery_capacity_kwh,
  range_km, range_standard,
  ac_charging_kw, dc_charging_kw, max_dc_fast_charging_kw, dc_fast_charging_30_80_min,
  v2l,
  max_power_kw, max_torque_nm, acceleration_0_100_s,
  drive_type, drive_modes
) values
  ('ALON UT',         'STANDARD',            549900, 4270, 1850, 1575, 2750, 5, 440,  1660, 1540, null, 'LFP',                44.12, 400, 'NEDC',  7,  87,  64, 24, true,  100, 145,  11.4, 'FWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('ALON UT',         'PREMIUM',             649900, 4270, 1850, 1575, 2750, 5, 440,  1660, 1700, null, 'LFP',                60.00, 500, 'NEDC',  7,  87,  87, 24, true,  150, 210,   7.3, 'FWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('BYD ATTO 3',      'PREMIUM',             949900, 4455, 1875, 1615, 2720, 5, 440,  1340, 1680, null, 'BYD Blade Battery',  50.25, 410, 'NEDC',  7,  70, 110, 35, true,  150, 310,   7.9, 'FWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('BYD ATTO 3',      'EXTENDED',           1049900, 4455, 1875, 1615, 2720, 5, 440,  1340, 1750, null, 'BYD Blade Battery',  60.48, 480, 'NEDC',  7,  88, 110, 35, true,  150, 310,   7.3, 'FWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('BYD SEALION 7',   'PREMIUM',            1249900, 4830, 1925, 1620, 2930, 5, 558,   null, 2225, null, 'BYD Blade Battery',  82.50, 567, 'NEDC', 11, 150, 150, 25, true,  230, 380,   6.7, 'RWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('BYD SEALION 7',   'AWD PERFORMANCE',    1399900, 4830, 1925, 1620, 2930, 5, 558,   null, 2340, null, 'BYD Blade Battery',  82.50, 542, 'NEDC', 11, 150, 150, 25, true,  380, 690,   4.5, 'AWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('GEELY EX2',       'PRO',                 399990, 4135, 1805, 1580, 2650, 5, 375,  1320, 1300, null, 'LFP',                40.80, 395, 'NEDC', 11, 150,  70, 25, true,   85, 150,  11.5, 'FWD',     ARRAY['ECO','COMFORT','SPORT']),
  ('GEELY EX2',       'MAX',                 429990, 4135, 1805, 1580, 2650, 5, 375,  1320, 1300, null, 'LFP',                40.80, 395, 'NEDC', 11, 150,  70, 25, true,   85, 150,  11.5, 'FWD',     ARRAY['ECO','COMFORT','SPORT']),
  ('GEELY EX5',       'PRO',                 699000, 4615, 1901, 1670, 2750, 5, 461,  1877, 1715, null, 'LFP',                60.22, 495, 'NEDC', 11, 150, 100, 20, true,  160, 320,   6.9, 'FWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('GEELY EX5',       'MAX',                 849000, 4615, 1901, 1670, 2750, 5, 461,  1877, 1765, null, 'LFP',                60.22, 490, 'NEDC', 11, 150, 100, 20, true,  160, 320,   7.1, 'FWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('JAECOO 6 EV',     'Long Range 2WD PRO',  899000, 4406, 1910, 1715, 2715, 5, 450,   null, 1820, null, 'LFP',                65.69, 426, 'NEDC',  6.6, 80, 80, 30, true,  135, 220,  10.5, 'FWD',     ARRAY['ECO','NORMAL','SPORT','CUSTOM']),
  ('JAECOO 6 EV',     'Long Range 2WD',     1099000, 4406, 1910, 1715, 2715, 5, 450,   null, 1800, null, 'LFP',                65.69, 426, 'NEDC',  6.6, 80, 80, 30, true,  135, 220,  10.5, 'FWD',     ARRAY['ECO','NORMAL','SPORT','CUSTOM']),
  ('JAECOO 6 EV',     'Long Range 4WD',     1249000, 4406, 1910, 1715, 2715, 5, 450,   null, 1975, null, 'LFP',                69.77, 418, 'NEDC',  6.6, 80, 80, 30, true,  205, 385,   6.5, 'AWD',     ARRAY['ECO','NORMAL','SPORT','CUSTOM','ALL ROAD','SLIPPERY','BEACH','MUDDY','BUMPY']),
  ('MG ZS',           'C+',                  659900, 4323, 1809, 1628, 2585, 5, 448,  1457, 1290, null, 'LFP',                50.30, 403, 'NEDC',  6.6, 92, 92, 30, true,   84, 150,   8.6, 'FWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('MG ZS',           'D',                   599000, 4324, 1809, 1653, 2585, 5, 448,  1457, 1290, null, 'LFP',                50.30, 403, 'NEDC',  6.6, 92, 92, 30, true,   84, 150,   8.6, 'FWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('MG ZS',           'X',                   649000, 4324, 1809, 1653, 2585, 5, 448,  1457, 1290, null, 'LFP',                50.30, 403, 'NEDC',  6.6, 92, 92, 30, true,   84, 150,   8.6, 'FWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('MG ZS',           'V',                   689000, 4324, 1809, 1653, 2585, 5, 448,  1457, 1290, null, 'LFP',                50.30, 403, 'NEDC',  6.6, 92, 92, 30, true,   84, 150,   8.6, 'FWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('MG 4 ELECTRIC',   '49 kWh D',            709900, 4287, 1836, 1516, 2750, 5, 363,   null, 1620, null, 'LFP',                49.00, 423, 'NEDC',  6.6,117, 117, 35, true,  125, 250,   7.7, 'RWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('MG 4 ELECTRIC',   'LONG RANGE',          769900, 4287, 1836, 1516, 2750, 5, 363,   null, 1675, null, 'LFP',                64.00, 540, 'NEDC',  6.6,140, 140, 35, true,  125, 250,   7.1, 'RWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('MG 4 ELECTRIC',   '64 kWh V',            769900, 4287, 1836, 1516, 2750, 5, 350,   363, 1751, null, 'LFP',                64.00, 540, 'NEDC',  6.6,140, 140, 35, true,  125, 250,   6.5, 'RWD',     ARRAY['ECO','NORMAL','SPORT','SNOW']),
  ('MG 4 ELECTRIC',   'XPOWER',             1119900, 4287, 1836, 1516, 2750, 5, 350,   363, 1800, 1803, 'LFP',                64.00, 480, 'NEDC', 11, 140, 140, 35, true,  320, 600,   3.8, 'AWD',     ARRAY['ECO','NORMAL','SPORT','SNOW','TRACK']),
  ('NETA V-II',        'LITE',               549000, 4070, 1690, 1540, 2420, 5, 335,   588, 1180, null, 'LFP',                36.10, 382, 'NEDC',  6.6,100, 100, 30, true,   70, 150,  12.0, 'FWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('NETA V-II',        'SMART',              569000, 4070, 1690, 1540, 2420, 5, 335,   588, 1180, null, 'LFP',                36.10, 382, 'NEDC',  6.6,100, 100, 30, true,   70, 150,  12.0, 'FWD',     ARRAY['ECO','NORMAL','SPORT']),
  ('TESLA MODEL 3',    null,                1149000, 4720, 1850, 1440, 2875, 5, 682,   null, 1760, 1851, 'Liquid-cooled Li-ion', 57.50, 534, 'WLTP', 11, 250, 175, 25, false, 208, 420,   6.2, 'RWD',     ARRAY['CHILL','STANDARD','SPORT']);
