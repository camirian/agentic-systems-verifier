package SpacecraftArchitecture {
    
    // Define the core battery subsystem blocks and their ports
    part def BatteryPack {
        attribute capacity: Real = 100.0 [kWh];
        attribute currentTemp: Real = 20.0 [C];
        port powerOut: PowerPort;
        port thermalInterface: ThermalPort;
    }

    part def ThermalControlSystem {
        attribute coolingCapacity: Real = 5.0 [kW];
        attribute targetTempMin: Real = 10.0 [C];
        attribute targetTempMax: Real = 25.0 [C];
        port thermalInterface: ThermalPort;
    }

    // Define the parent system assembling the parts
    part def PowerAndThermalSubsystem {
        part battery: BatteryPack;
        part tcs: ThermalControlSystem;
        
        // Internal Block connections
        connect battery.thermalInterface to tcs.thermalInterface;
    }

    // Requirements formalization
    requirement def BatteryThermalRequirement {
        doc /* The thermal control system shall maintain the battery temperature 
               between 10C and 25C during all operational phases. */
        attribute minTemp: Real = 10.0 [C];
        attribute maxTemp: Real = 25.0 [C];
    }
    
    // Satisfy relationship representing traceability
    satisfy requirement BatteryThermalRequirement by part PowerAndThermalSubsystem;
}
