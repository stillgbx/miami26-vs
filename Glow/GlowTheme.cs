using System;
using Microsoft.VisualStudio.PlatformUI;
using Microsoft.VisualStudio.Shell;

namespace Miami26VS.Glow
{
    /// <summary>
    /// Tells whether the active theme wants the glow: only the dark Miami '26 themes define the
    /// Miami26/NeonGlow color (see tools/generate-themes.py).
    /// </summary>
    internal static class GlowTheme
    {
        private static readonly ThemeResourceKey Marker =
            new ThemeResourceKey(new Guid("a66c2731-f386-4130-813d-a705e4dc1880"), "NeonGlow", ThemeResourceKeyType.BackgroundColor);

        public static bool IsActive
        {
            get
            {
                ThreadHelper.ThrowIfNotOnUIThread();
                try
                {
                    return VSColorTheme.GetThemedColor(Marker).A != 0;
                }
                catch (Exception)
                {
                    return false;
                }
            }
        }
    }
}
