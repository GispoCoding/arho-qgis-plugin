// Home page hexagons: draw the hexagon under the mouse on top of the others.
//
// A hovered hexagon grows, and a ring in the band colour keeps the normal gap
// around it (gispo.css). The ring must cover the edges of the neighbours, but
// SVG draws shapes in document order and has no z-index. So the hovered
// hexagon moves to the end of the field.
// One listener on the document, so it still works after instant navigation.
document.addEventListener("pointerover", (event) => {
  if (event.pointerType !== "mouse" || !(event.target instanceof SVGPolygonElement)) {
    return;
  }
  const hexagon = event.target;
  const field = hexagon.closest(".arho-hexes");
  if (field && hexagon !== field.lastElementChild) {
    field.append(hexagon);
  }
});
