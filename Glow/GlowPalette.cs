using System.Collections.Generic;
using System.Windows.Media;

namespace Miami26VS.Glow
{
    /// <summary>One layer of a CSS text-shadow: "0 0 {Blur}px {Color}".</summary>
    internal readonly struct GlowShadow
    {
        public GlowShadow(double blur, Color color, bool neon)
        {
            Blur = blur;
            Color = color;
            Neon = neon;
        }

        public double Blur { get; }

        public Color Color { get; }

        /// <summary>Neon layers take their opacity from the brightness option, from 0 to 1.</summary>
        public bool Neon { get; }

        public Color WithBrightness(double brightness) =>
            Neon ? Color.FromArgb((byte)(brightness * 255), Color.R, Color.G, Color.B) : Color;
    }

    /// <summary>
    /// The neon text-shadows of the dark Miami '26 themes, as CSS "0 0 {blur}px {color}" layers, keyed by
    /// the token color they apply to. tools/generate-themes.py checks that these keys match the palettes.
    /// </summary>
    internal static class GlowPalette
    {
        private static readonly Dictionary<Color, GlowShadow[]> Shadows = new Dictionary<Color, GlowShadow[]>
        {
            // Miami '26 Bay
            [Rgb(0x2ED3C6)] = new[] { Dark(2, 0x041210), Neon(4, 0x00E5D4), Neon(10, 0x00E5D4) },   // Keywords: turquoise
            [Rgb(0xB9A6FF)] = new[] { Dark(2, 0x0E0A1F), Neon(4, 0x8C6CFF), Neon(10, 0x8C6CFF) },   // Types: lavender
            [Rgb(0x7CC4FF)] = new[] { Dark(2, 0x04101F), Neon(3, 0x2E9BFF), Neon(8, 0x2E9BFF) },    // Functions: sky
            [Rgb(0x7EDC9E)] = new[] { Dark(2, 0x0C100C), Neon(8, 0x2FB86A), Neon(24, 0x1E3A2A) },   // Tags: palm green
            [Rgb(0xDCEBF5)] = new[] { Dark(2, 0x0C1B26), Fixed(5, 0x33, 0x7CC4FF), Fixed(10, 0x22, 0xFFFFFF) }, // Variables

            // Miami '26 Sunset
            [Rgb(0xFF4FA3)] = new[] { Dark(2, 0x2A0A1A), Neon(4, 0xFF2E93), Neon(10, 0xFF2E93) },   // Keywords: magenta
            [Rgb(0xA9B4F5)] = new[] { Dark(2, 0x0A0C24), Neon(4, 0x6F7BFF), Neon(10, 0x6F7BFF) },   // Types: periwinkle
            [Rgb(0xFFA45C)] = new[] { Dark(2, 0x1A0E00), Neon(3, 0xFF7A1F), Neon(8, 0xFF7A1F) },    // Functions: sunset orange
            [Rgb(0xD39BFF)] = new[] { Dark(2, 0x120A1C), Neon(8, 0xA44CFF), Neon(24, 0x2A1A3A) },   // Tags: violet
            [Rgb(0xF3DDF0)] = new[] { Dark(2, 0x15112A), Fixed(5, 0x33, 0xFF4FA3), Fixed(10, 0x22, 0xFFFFFF) }, // Variables
        };

        public static bool TryGetShadows(Color text, out GlowShadow[] shadows) =>
            Shadows.TryGetValue(Color.FromRgb(text.R, text.G, text.B), out shadows);

        private static GlowShadow Dark(double blur, int rgb) => new GlowShadow(blur, Rgb(rgb), false);

        private static GlowShadow Neon(double blur, int rgb) => new GlowShadow(blur, Rgb(rgb), true);

        private static GlowShadow Fixed(double blur, byte alpha, int rgb)
        {
            Color color = Rgb(rgb);
            return new GlowShadow(blur, Color.FromArgb(alpha, color.R, color.G, color.B), false);
        }

        private static Color Rgb(int rgb) => Color.FromRgb((byte)(rgb >> 16), (byte)(rgb >> 8), (byte)rgb);
    }
}
