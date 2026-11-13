using System;
using System.Collections.Generic;
using System.Linq;

namespace Miami
{
    /// <summary>A car cruising down Ocean Drive.</summary>
    public sealed class Ride
    {
        public Ride(string model, string color, int topSpeed)
        {
            Model = model;
            Color = color;
            TopSpeed = topSpeed;
        }

        public string Model { get; }

        public string Color { get; }

        public int TopSpeed { get; }
    }

    public sealed class OceanDrive
    {
        private const int MaxCruisers = 8;
        private readonly List<Ride> cruisers = new List<Ride>();

        public OceanDrive(string night) => Night = night;

        public string Night { get; }

        public Ride Fastest => cruisers.OrderByDescending(ride => ride.TopSpeed).FirstOrDefault();

        // The strip only fits so many cars after sunset.
        public bool Cruise(Ride ride)
        {
            if (ride == null || cruisers.Count >= MaxCruisers)
            {
                return false;
            }

            cruisers.Add(ride);
            return true;
        }

        public override string ToString() => $"{Night}: {cruisers.Count} cars, fastest {Fastest?.Model ?? "none"}";

        public static void Main()
        {
            var drive = new OceanDrive("Friday \"neon\" night\n");
            drive.Cruise(new Ride("Roadster", "Hot pink", 290));
            drive.Cruise(new Ride("Convertible", "Sunset orange", 260));
            Console.WriteLine(drive);
        }
    }
}
