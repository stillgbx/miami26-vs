using System.Runtime.InteropServices;
using Microsoft.VisualStudio.Shell;
using Miami26VS.Glow;

namespace Miami26VS
{
    /// <summary>
    /// Only registers the options page: VS loads the package when the page is opened.
    /// </summary>
    [PackageRegistration(UseManagedResourcesOnly = true, AllowsBackgroundLoading = true)]
    [Guid("eaca3a58-ea1d-4a38-aee7-6974b6214c90")]
    [ProvideOptionPage(typeof(GlowOptionsPage), "Miami '26", "Neon Glow", 0, 0, true)]
    public sealed class Miami26Package : AsyncPackage
    {
    }
}
