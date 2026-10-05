-- Synthetic demo data only. Do not add production records, credentials, audio, or transcripts.

insert into public.reservations (
  id,
  reservation_code,
  guest_display_name,
  arrival_date,
  departure_date,
  room_number,
  status
)
values
  (
    '11111111-1111-4111-8111-111111111111',
    'DEMO-EN-1001',
    'Alex Demo',
    current_date,
    current_date + 2,
    '101',
    'reserved'
  ),
  (
    '22222222-2222-4222-8222-222222222222',
    'DEMO-VI-1002',
    'Minh Demo',
    current_date,
    current_date + 3,
    '202',
    'reserved'
  ),
  (
    '33333333-3333-4333-8333-333333333333',
    'DEMO-CHECKED-IN',
    'Jordan Demo',
    current_date - 1,
    current_date + 1,
    '303',
    'checked_in'
  ),
  (
    '44444444-4444-4444-8444-444444444444',
    'DEMO-CANCELLED',
    'Taylor Demo',
    current_date + 7,
    current_date + 9,
    null,
    'cancelled'
  )
on conflict (id) do nothing;

insert into public.bills (
  id,
  reservation_id,
  items,
  currency,
  total_amount_minor,
  status
)
values
  (
    'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
    '11111111-1111-4111-8111-111111111111',
    '[
      {"description": "Demo room night", "quantity": 2, "unitAmountMinor": 12500, "lineTotalMinor": 25000},
      {"description": "Demo breakfast", "quantity": 2, "unitAmountMinor": 1800, "lineTotalMinor": 3600}
    ]'::jsonb,
    'CAD',
    28600,
    'open'
  ),
  (
    'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2',
    '22222222-2222-4222-8222-222222222222',
    '[
      {"description": "Đêm phòng mẫu", "quantity": 3, "unitAmountMinor": 12500, "lineTotalMinor": 37500},
      {"description": "Bữa sáng mẫu", "quantity": 3, "unitAmountMinor": 1800, "lineTotalMinor": 5400}
    ]'::jsonb,
    'CAD',
    42900,
    'open'
  ),
  (
    'cccccccc-cccc-4ccc-8ccc-ccccccccccc3',
    '33333333-3333-4333-8333-333333333333',
    '[
      {"description": "Demo room night", "quantity": 1, "unitAmountMinor": 12500, "lineTotalMinor": 12500}
    ]'::jsonb,
    'CAD',
    12500,
    'open'
  )
on conflict (id) do nothing;
