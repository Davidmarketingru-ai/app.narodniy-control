# Test Credentials

## Authentication
- Login via Google Auth (no email/password)
- Admin access: manually set `role: "admin"` in MongoDB `users` collection

## Test Tokens (for API testing)
- User 1 (David Marketing, chairman council_766c80223222): `Bearer WRANhsgZEBRoK2GSyIUvBEaqIWo0YtmhTsICy2Y4cPc`
  - user_id: user_eec305b08f9c, address: Ленина 15, Октябрьский, Бишкек

- User 2 (Тест Пользователь 2): `Bearer qaiAgO3W1YY2ZRN-5c2wk2BrNaGBNVE_rfYAxlye9cI`
  - user_id: test-user-council-2, address: Ленина 15

- User House2 (chairman council_0c4b7a580b9d): `Bearer xvLTdXAyTaWU6uzqMo2NMpdrnqwuxIfGtlf_66FbhN4`
  - user_id: test-user-house2, address: Ленина 20

- User c3: `Bearer 2T7204cjRXDL33bknasoPH6BZxNu9GsSAMGuWA5TCOM`
  - user_id: test-user-c3

## Test Data
- Council 1 (yard, formed 100%): council_766c80223222
- Council 2 (yard): council_0c4b7a580b9d
- District Council (via escalation): council_0a5d54fc20a6
