(add_person
  (firstName != "")
  (lastName != "")
  (check_length (max firstName 50))
  (check_length (max lastName 50))))
