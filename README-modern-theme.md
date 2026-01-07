# Intégration du thème moderne

1. Placez `modern-theme.css` dans votre dossier statique (ex. `static/css/`).
2. Ajoutez la balise suivante dans vos templates (ex. `base.html`) **sans modifier le HTML existant** :

```html
<link rel="stylesheet" href="/static/css/modern-theme.css">
```

3. Vérifiez :
   - Contrastes lisibles, focus visible sur liens/boutons/champs.
   - Responsive : navigation wrap sur mobile, paddings ajustés.
   - Pas de changement de structure (classes/IDs/balises inchangés).

4. Retour arrière : supprimez simplement la balise `<link>` ou retirez le fichier du dossier statique.
