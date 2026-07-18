# Moteur de diagnostic

Chaque propriété d’une caméra est stockée comme un `DiagnosticFact` avec une valeur,
un niveau de preuve, une source facultative et une note facultative.

Les niveaux sont `confirmed`, `observed`, `hypothesis` et `unknown`.
`unknown` est la valeur par défaut : une capacité non testée ne peut jamais être
présentée silencieusement comme prise en charge.
