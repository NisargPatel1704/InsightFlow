// ---------------------------------------------------------------------------
// InsightFlow — core client behavior
// ---------------------------------------------------------------------------

(function () {
  const html = document.documentElement;
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

  // ---- Theme toggle -------------------------------------------------------
  const themeBtn = document.getElementById('themeToggle');
  const sunIcon = document.getElementById('themeIconSun');
  const moonIcon = document.getElementById('themeIconMoon');

  function reflectThemeIcons() {
    const isDark = html.getAttribute('data-theme') === 'dark';
    if (sunIcon && moonIcon) {
      sunIcon.style.display = isDark ? 'none' : 'block';
      moonIcon.style.display = isDark ? 'block' : 'none';
    }
  }
  reflectThemeIcons();

  if (themeBtn) {
    themeBtn.addEventListener('click', async () => {
      const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      // Reflect instantly so the toggle feels responsive even before the reload.
      html.setAttribute('data-theme', newTheme);
      reflectThemeIcons();
      themeBtn.disabled = true;
      themeBtn.style.opacity = '0.5';
      try {
        await fetch('/theme/toggle', {
          method: 'POST',
          headers: { 'X-CSRFToken': csrfToken },
        });
      } catch (err) {
        console.warn('Theme preference could not be saved.', err);
      } finally {
        // Reload so any Chart.js canvases on the page re-render with the
        // correct theme colors (Chart.js bakes colors in at draw time).
        window.location.reload();
      }
    });
  }

  // ---- Mobile sidebar toggle ------------------------------------------------
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', (e) => {
      if (
        sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        !sidebarToggle.contains(e.target)
      ) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ---- Auto-dismiss flash alerts -------------------------------------------
  document.querySelectorAll('#alertStack .alert').forEach((alertEl, idx) => {
    setTimeout(() => {
      alertEl.style.transition = 'opacity 240ms ease, transform 240ms ease';
      alertEl.style.opacity = '0';
      alertEl.style.transform = 'translateX(16px)';
      setTimeout(() => alertEl.remove(), 260);
    }, 4500 + idx * 200);
  });

  // ---- Chart.js shared theme helper ----------------------------------------
  window.InsightFlowCharts = {
    getColors() {
      const styles = getComputedStyle(document.documentElement);
      return {
        accent: styles.getPropertyValue('--color-accent').trim(),
        accentSoft: styles.getPropertyValue('--color-accent-soft').trim(),
        positive: styles.getPropertyValue('--color-positive').trim(),
        warning: styles.getPropertyValue('--color-warning').trim(),
        danger: styles.getPropertyValue('--color-danger').trim(),
        info: styles.getPropertyValue('--color-info').trim(),
        surface: styles.getPropertyValue('--color-surface').trim(),
        textSecondary: styles.getPropertyValue('--color-text-secondary').trim(),
        border: styles.getPropertyValue('--color-border').trim(),
        mono: styles.getPropertyValue('--font-mono').trim(),
        ui: styles.getPropertyValue('--font-ui').trim(),
      };
    },
    baseGridOptions(colors) {
      return {
        grid: { color: colors.border, drawTicks: false },
        ticks: { color: colors.textSecondary, font: { family: colors.ui, size: 11 } },
        border: { display: false },
      };
    },
  };

  window.csrfToken = csrfToken;

  // ---- Global Chart.js presentation defaults ---------------------------
  // Applied once here so every chart across the app gets a consistent,
  // premium look (smooth entrance animation + polished tooltips) without
  // repeating this config in every template.
  if (window.Chart) {
    try {
      const styles = getComputedStyle(document.documentElement);
      const surface = styles.getPropertyValue('--color-surface').trim();
      const textPrimary = styles.getPropertyValue('--color-text-primary').trim();
      const textSecondary = styles.getPropertyValue('--color-text-secondary').trim();
      const border = styles.getPropertyValue('--color-border').trim();
      const uiFont = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";

      Chart.defaults.font.family = uiFont;
      Chart.defaults.font.size = 12;
      Chart.defaults.color = textSecondary;
      Chart.defaults.animation = { duration: 700, easing: 'easeOutQuart' };

      Chart.defaults.plugins.tooltip.enabled = true;
      Chart.defaults.plugins.tooltip.backgroundColor = surface;
      Chart.defaults.plugins.tooltip.titleColor = textPrimary;
      Chart.defaults.plugins.tooltip.bodyColor = textSecondary;
      Chart.defaults.plugins.tooltip.borderColor = border;
      Chart.defaults.plugins.tooltip.borderWidth = 1;
      Chart.defaults.plugins.tooltip.padding = 10;
      Chart.defaults.plugins.tooltip.cornerRadius = 10;
      Chart.defaults.plugins.tooltip.boxPadding = 5;
      Chart.defaults.plugins.tooltip.titleFont = { family: uiFont, size: 12, weight: '600' };
      Chart.defaults.plugins.tooltip.bodyFont = { family: uiFont, size: 12 };
      Chart.defaults.plugins.tooltip.displayColors = true;
      Chart.defaults.plugins.tooltip.usePointStyle = true;
    } catch (err) {
      console.warn('Chart.js default styling could not be fully applied.', err);
    }
  }
})();
