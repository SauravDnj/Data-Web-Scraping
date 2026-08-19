# Task Matrix

  Task       Depends on      Main output          Test level
  ---------- --------------- -------------------- ------------------
  T000       ---             Repo foundation      structural
  T001       T000            Coding rules         CI
  T002       T001            CI                   CI
  T010       T000            Python               smoke
  T011       T000            Next.js              smoke
  T012       T000            MySQL                integration
  T013       T000            Redis                integration
  T014       T010,T012       FastAPI              API
  T015       T010,T013       Worker               smoke
  T020       T012            SQLAlchemy           unit
  T021       T020            Alembic              migration
  T022-026   T021            Schema               integration
  T030       T022-026        Domain               unit
  T031       T030            State machine        unit
  T032       T020            Repositories         integration
  T033-039   T030-032        Services/API         API/integration
  T040       T030            Provider interface   unit
  T041-044   T040            Google adapter       contract
  T045       T041-044        Provider tests       contract
  T050-055   T030,T022-026   Pipeline             unit/integration
  T060       T015,T013       Queue                integration
  T061-065   T060,T035       Worker               integration
  T070-078   T033-039        UI                   component/E2E
  T080-085   T036,T061       Operations           integration
  T090-094   all             Quality              E2E/security
  T100-103   all             Release              operational
