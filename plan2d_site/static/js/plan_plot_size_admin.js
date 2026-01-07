(function () {
  const FACTOR = 3.28084;

  function sanitize(value) {
    return value
      .toLowerCase()
      .replace(/×/g, 'x')
      .replace(/meters?|metres?|meter|metre/g, '')
      .replace(/\s+/g, '')
      .replace(/m/g, '');
  }

  function parsePlotSize(value) {
    if (!value) {
      return null;
    }
    const normalized = sanitize(value);
    const match = normalized.match(/^(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)$/);
    if (!match) {
      return null;
    }
    const width = parseFloat(match[1]);
    const depth = parseFloat(match[2]);
    if (!Number.isFinite(width) || !Number.isFinite(depth) || width <= 0 || depth <= 0) {
      return null;
    }
    return { width, depth };
  }

  function toFeet(value) {
    return Math.round(value * FACTOR * 100) / 100;
  }

  function formatFeet(width, depth) {
    return `${width.toFixed(2)} ft x ${depth.toFixed(2)} ft`;
  }

  function updateDisplay(input, output) {
    const parsed = parsePlotSize(input.value);
    if (parsed) {
      const widthFt = toFeet(parsed.width);
      const depthFt = toFeet(parsed.depth);
      output.textContent = formatFeet(widthFt, depthFt);
      output.classList.remove('plot-size-ft-display--empty');
    } else {
      output.textContent = output.getAttribute('data-empty-label') || '—';
      output.classList.add('plot-size-ft-display--empty');
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('id_suggested_plot_size');
    const output = document.getElementById('id_suggested_plot_size_ft_display');
    if (!input || !output) {
      return;
    }
    const handler = updateDisplay.bind(null, input, output);
    ['input', 'change', 'blur', 'keyup'].forEach(function (eventName) {
      input.addEventListener(eventName, handler);
    });
    handler();
  });
})();
