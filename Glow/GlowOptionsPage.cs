using System.ComponentModel;
using System.Runtime.InteropServices;
using Microsoft.VisualStudio.Shell;

namespace Miami26VS.Glow
{
    [Guid("073e88e4-6e00-4291-8367-e10684870b0f")]
    public class GlowOptionsPage : DialogPage
    {
        [Category("Neon glow")]
        [DisplayName("Enable glow")]
        [Description("Draw the neon glow around the text when a dark Miami '26 theme is active (Bay or Sunset).")]
        [DefaultValue(GlowSettings.DefaultEnabled)]
        public bool Enabled { get; set; } = GlowSettings.DefaultEnabled;

        [Category("Neon glow")]
        [DisplayName("Brightness")]
        [Description("Glow intensity, from 0 to 100.")]
        [DefaultValue(GlowSettings.DefaultBrightness)]
        public int Brightness { get; set; } = GlowSettings.DefaultBrightness;

        public override void LoadSettingsFromStorage()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            Enabled = GlowSettings.Enabled;
            Brightness = GlowSettings.Brightness;
        }

        public override void SaveSettingsToStorage()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            GlowSettings.Save(Enabled, Brightness);
        }
    }
}
