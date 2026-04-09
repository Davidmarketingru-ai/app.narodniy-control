# Test Credentials

## Authentication
- Login via Google Auth (no email/password)
- Admin: user_eec305b08f9c has role "admin" (set via MongoDB)

## Test Tokens
- User 1 (admin, chairman council_766c80223222): `Bearer WRANhsgZEBRoK2GSyIUvBEaqIWo0YtmhTsICy2Y4cPc`
  - user_id: user_eec305b08f9c, address: Ленина 15, Октябрьский, Бишкек

- User 2: `Bearer qaiAgO3W1YY2ZRN-5c2wk2BrNaGBNVE_rfYAxlye9cI`
  - user_id: test-user-council-2

- User House2 (chairman council_0c4b7a580b9d): `Bearer xvLTdXAyTaWU6uzqMo2NMpdrnqwuxIfGtlf_66FbhN4`
  - user_id: test-user-house2

## Test Data
- Yard Councils: council_766c80223222 (formed 100%), council_0c4b7a580b9d
- District Council (via escalation): council_0a5d54fc20a6
- Org: org_seed_001

## Public Pages (no auth)
- /stats — public statistics
- /org/{orgId} — public org pages
