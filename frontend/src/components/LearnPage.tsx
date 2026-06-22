import './LearnPage.css';

interface Formula {
  name: string;
  symbol: string;
  expression: string;
  description: string;
  reference: string;
  implemented: boolean;
}

interface InstabilityGuide {
  indicator: string;
  values: { range: string; interpretation: string; color: string }[];
}

function LearnPage() {
  const formulas: Formula[] = [
    {
      name: 'Dew Point Temperature',
      symbol: 'Td',
      expression: 'Td = (b × α) / (a − α)\nwhere α = ln(RH/100) + (a × T) / (b + T)',
      description:
        'The Magnus-Tetens formula estimates the temperature at which air becomes saturated with water vapor. When air cools to its dew point, condensation begins — forming dew, fog, or clouds.',
      reference: 'Magnus, G. (1844). Versuche über die Spannkräfte des Wasserdampfs. Annalen der Physik, 137(2), 225-247.',
      implemented: true,
    },
    {
      name: 'Dew Point Spread',
      symbol: 'T − Td',
      expression: 'Spread = Temperature − Dew Point',
      description:
        'The difference between air temperature and dew point. A small spread (< 2°C) indicates near-saturation and possible fog or precipitation. A large spread (> 5°C) indicates dry air and stable conditions.',
      reference: 'Ahrens, C.D. (2012). Meteorology Today: An Introduction to Weather, Climate, and the Environment.',
      implemented: true,
    },
    {
      name: 'Equivalent Potential Temperature',
      symbol: 'θe',
      expression: 'θe = θ × exp[(3.376 / TL) × r × (1 + 0.00081 × r)]\nwhere θ = potential temperature, TL = temperature at LCL, r = mixing ratio',
      description:
        'Theta-E represents the temperature an air parcel would have if all its moisture were condensed out and the latent heat used to warm the parcel, then brought dry-adiabatically to 1000 hPa. It is conserved during both dry and moist adiabatic processes, making it valuable for air mass identification.',
      reference: 'Bolton, D. (1980). The computation of equivalent potential temperature. Monthly Weather Review, 108(7), 1046-1053.',
      implemented: true,
    },
    {
      name: 'Lifted Index (Surface-Based Proxy)',
      symbol: 'LIproxy',
      expression: 'LI_proxy = T_env_5km − T_parcel_5km\nwhere T_env = T − (6.5 × 5) and T_parcel = T − (9.8 × 5)',
      description:
        'The Lifted Index measures atmospheric stability by comparing the temperature of a lifted surface parcel to the environmental temperature at ~5 km. Negative values indicate instability; values below −3 suggest potential for severe convection.',
      reference: 'Doswell, C.A., & Rasmussen, E.N. (1994). The effect of neglecting the virtual temperature correction on CAPE calculations. Weather and Forecasting, 9(4), 625-629.',
      implemented: true,
    },
    {
      name: 'CAPE Proxy',
      symbol: 'CAPEproxy',
      expression: 'CAPE_proxy = buoyancy × scaling_factor\nwhere buoyancy = T_parcel − T_env at 500 hPa',
      description:
        'Convective Available Potential Energy (CAPE) quantifies the energy available for convection. True CAPE requires upper-air sounding data. This surface-based proxy uses a standard lapse rate assumption to estimate convective potential from surface observations alone.',
      reference: 'Doswell, C.A., & Rasmussen, E.N. (1994). Weather and Forecasting, 9(4), 625-629.',
      implemented: true,
    },
    {
      name: 'Convective Temperature',
      symbol: 'Tconv',
      expression: 'T_conv ≈ Td + (T − Td) × (1.2 + dry_factor × 0.8)\nwhere dry_factor = (100 − RH) / 100',
      description:
        'The surface temperature that must be reached for free convection to occur without mechanical lifting. When the actual temperature approaches the convective temperature, cumulus cloud formation becomes likely.',
      reference: 'Stull, R. (2017). Practical Meteorology: An Algebra-based Survey of Atmospheric Science.',
      implemented: true,
    },
    {
      name: 'Rainfall Probability',
      symbol: 'P(rain)',
      expression: 'Multi-factor weighted score:\n• Humidity > 90%: +30 pts\n• Dew spread < 1°C: +35 pts\n• Pressure falling > 1.5 hPa/hr: +25 pts\n• LI proxy < −3: +10 pts\nScore capped at 95%',
      description:
        'A heuristic probability estimator combining moisture, instability, and pressure tendency indicators. Not a formal forecast, but provides a data-driven assessment of conditions favorable for precipitation.',
      reference: 'Adapted from multi-parameter nowcasting approaches (World Meteorological Organization, 2017).',
      implemented: true,
    },
    {
      name: 'Pressure Tendency Classification',
      symbol: 'ΔP/Δt',
      expression: 'ΔP = P_current − P_previous (smoothed over 15-min window)',
      description:
        'WMO-style pressure tendency categorisation. Falling pressure typically indicates approaching weather systems; rising pressure suggests improving conditions. Combined with humidity trends, it helps identify potential atmospheric disturbances.',
      reference: 'World Meteorological Organization (2018). Guide to Meteorological Instruments and Methods of Observation (WMO-No. 8).',
      implemented: true,
    },
    {
      name: 'Clausius-Clapeyron Relation',
      symbol: 'd(es)/dT',
      expression: 'Water-holding capacity increases ~6–7% per 1°C warming.\ndes/dT = (L × es) / (Rv × T²)',
      description:
        'Describes how the atmosphere\'s capacity to hold water vapor increases with temperature. This relationship explains why warmer climates experience more intense rainfall events — warmer air can hold more moisture before saturation.',
      reference: 'Clausius, R. (1850). Über die bewegende Kraft der Wärme. Annalen der Physik, 155(3), 368-397.',
      implemented: false,
    },
    {
      name: 'Virtual Temperature',
      symbol: 'Tv',
      expression: 'Tv = T × (1 + 0.61 × w)\nwhere w = mixing ratio (kg/kg)',
      description:
        'The temperature dry air would need to have the same density as moist air at the same pressure. Used in buoyancy calculations because water vapor is lighter than dry air.',
      reference: 'Stull, R. (2017). Practical Meteorology.',
      implemented: false,
    },
    {
      name: 'Wet-Bulb Temperature',
      symbol: 'Tw',
      expression: 'Tw ≈ T × atan[0.151977(RH+8.313659)^0.5] + atan(T+RH)\n− atan(RH−1.676331) + 0.00391838(RH)^1.5 × atan(0.023101RH)\n− 4.686035',
      description:
        'The lowest temperature air can reach through evaporative cooling. Important for understanding heat stress, snow-making conditions, and cooling tower efficiency.',
      reference: 'Stull, R. (2011). Wet-bulb temperature from relative humidity and air temperature. Journal of Applied Meteorology and Climatology, 50(11), 2267-2269.',
      implemented: false,
    },
  ];

  const instabilityGuides: InstabilityGuide[] = [
    {
      indicator: 'Dew Point Spread',
      values: [
        { range: '< 2 °C', interpretation: 'Near saturation. Fog, low clouds, or precipitation likely.', color: '#dc3545' },
        { range: '2 – 5 °C', interpretation: 'Moderate moisture. Partly cloudy conditions possible.', color: '#ffc107' },
        { range: '> 5 °C', interpretation: 'Dry air mass. Clear skies and stable conditions.', color: '#28a745' },
      ],
    },
    {
      indicator: 'Lifted Index (Proxy)',
      values: [
        { range: '< −3 °C', interpretation: 'Strongly unstable. Potential for severe convection.', color: '#dc3545' },
        { range: '−3 to −1 °C', interpretation: 'Marginally unstable. Scattered showers possible.', color: '#ffc107' },
        { range: '> −1 °C', interpretation: 'Stable. Convection unlikely.', color: '#28a745' },
      ],
    },
    {
      indicator: 'Theta-E',
      values: [
        { range: '> 350 K', interpretation: 'High moist static energy. Favorable for deep convection.', color: '#dc3545' },
        { range: '330 – 350 K', interpretation: 'Moderate energy. Typical of warm sector air masses.', color: '#ffc107' },
        { range: '< 330 K', interpretation: 'Low energy. Stable or cool air mass.', color: '#28a745' },
      ],
    },
    {
      indicator: 'CAPE Proxy',
      values: [
        { range: '> 1500 J/kg', interpretation: 'Moderate to high instability. Thunderstorms possible.', color: '#dc3545' },
        { range: '500 – 1500 J/kg', interpretation: 'Marginal instability. Weak convection possible.', color: '#ffc107' },
        { range: '< 500 J/kg', interpretation: 'Stable or weakly unstable.', color: '#28a745' },
      ],
    },
    {
      indicator: 'Pressure Tendency',
      values: [
        { range: 'Falling > 1 hPa/hr', interpretation: 'Approaching disturbance. Potential for deteriorating weather.', color: '#dc3545' },
        { range: 'Steady', interpretation: 'No significant change expected in the near term.', color: '#ffc107' },
        { range: 'Rising > 1 hPa/hr', interpretation: 'Improving conditions. High pressure building.', color: '#28a745' },
      ],
    },
    {
      indicator: 'Rainfall Probability',
      values: [
        { range: '> 70%', interpretation: 'High likelihood. Conditions strongly favor precipitation.', color: '#2196f3' },
        { range: '40 – 70%', interpretation: 'Moderate chance. Monitor conditions for changes.', color: '#ff9800' },
        { range: '< 40%', interpretation: 'Low likelihood. Significant precipitation not expected.', color: '#4caf50' },
      ],
    },
  ];

  return (
    <div className="learn-page">
      <div className="learn-header">
        <h1>📚 Atmospheric Science Reference</h1>
        <p className="learn-subtitle">
          Understanding the physics behind microclimate monitoring and atmospheric instability detection
        </p>
      </div>

      <section className="learn-section">
        <h2>📐 Formulas Implemented in This System</h2>
        <div className="formulas-grid">
          {formulas
            .filter((f) => f.implemented)
            .map((formula, index) => (
              <div key={index} className="formula-card implemented">
                <div className="formula-header">
                  <h3>{formula.name}</h3>
                  <span className="formula-symbol">{formula.symbol}</span>
                </div>
                <pre className="formula-expression">{formula.expression}</pre>
                <p className="formula-description">{formula.description}</p>
                <p className="formula-reference">📖 {formula.reference}</p>
              </div>
            ))}
        </div>
      </section>

      <section className="learn-section">
        <h2>🔬 Additional Atmospheric Formulas</h2>
        <p className="section-note">
          These formulas are fundamental to atmospheric science but not directly computed in this system.
          They are included for educational completeness.
        </p>
        <div className="formulas-grid">
          {formulas
            .filter((f) => !f.implemented)
            .map((formula, index) => (
              <div key={index} className="formula-card not-implemented">
                <div className="formula-header">
                  <h3>{formula.name}</h3>
                  <span className="formula-symbol">{formula.symbol}</span>
                </div>
                <pre className="formula-expression">{formula.expression}</pre>
                <p className="formula-description">{formula.description}</p>
                <p className="formula-reference">📖 {formula.reference}</p>
              </div>
            ))}
        </div>
      </section>

      <section className="learn-section">
        <h2>📊 Interpretation Guide: Instability Indicators</h2>
        <p className="section-note">
          How to interpret the atmospheric indicators displayed on the dashboard
        </p>
        <div className="guides-grid">
          {instabilityGuides.map((guide, index) => (
            <div key={index} className="guide-card">
              <h3>{guide.indicator}</h3>
              <table className="guide-table">
                <thead>
                  <tr>
                    <th>Range</th>
                    <th>Interpretation</th>
                  </tr>
                </thead>
                <tbody>
                  {guide.values.map((v, i) => (
                    <tr key={i}>
                      <td>
                        <span className="range-badge" style={{ background: v.color }}>
                          {v.range}
                        </span>
                      </td>
                      <td>{v.interpretation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      </section>

      <section className="learn-section">
        <h2>🎓 Key Meteorological Concepts</h2>
        <div className="concepts-grid">
          <div className="concept-card">
            <h3>Atmospheric Stability</h3>
            <p>
              A measure of the atmosphere's resistance to vertical motion. Stable air resists upward
              movement; unstable air promotes it. Stability is determined by comparing the temperature
              of a rising air parcel to its surroundings.
            </p>
          </div>
          <div className="concept-card">
            <h3>Convection</h3>
            <p>
              Vertical transport of heat and moisture driven by buoyancy. Warm, moist air near the
              surface rises, cools, and may condense into clouds. Sufficient instability leads to
              thunderstorms.
            </p>
          </div>
          <div className="concept-card">
            <h3>Boundary Layer</h3>
            <p>
              The lowest part of the atmosphere (typically 0-2 km) directly influenced by the Earth's
              surface. Most weather phenomena affecting human activity occur within this layer.
            </p>
          </div>
          <div className="concept-card">
            <h3>Moist Static Energy</h3>
            <p>
              The combined thermal, potential, and latent energy of an air parcel. Theta-E quantifies
              this energy and helps identify air masses capable of producing deep convection.
            </p>
          </div>
          <div className="concept-card">
            <h3>Microclimate</h3>
            <p>
              Local atmospheric conditions that differ from the surrounding regional climate. Buildings,
              vegetation, water bodies, and topography all influence microclimates.
            </p>
          </div>
          <div className="concept-card">
            <h3>Saturation</h3>
            <p>
              The state at which air holds the maximum possible water vapor at a given temperature.
              Further cooling or moisture addition results in condensation — forming dew, fog, or clouds.
            </p>
          </div>
        </div>
      </section>

      <section className="learn-section">
        <h2>📖 References & Further Reading</h2>
        <ul className="references-list">
          <li>Bolton, D. (1980). The computation of equivalent potential temperature. <em>Monthly Weather Review</em>, 108(7), 1046-1053.</li>
          <li>Doswell, C.A., & Rasmussen, E.N. (1994). The effect of neglecting the virtual temperature correction on CAPE calculations. <em>Weather and Forecasting</em>, 9(4), 625-629.</li>
          <li>Magnus, G. (1844). Versuche über die Spannkräfte des Wasserdampfs. <em>Annalen der Physik</em>, 137(2), 225-247.</li>
          <li>Stull, R. (2017). <em>Practical Meteorology: An Algebra-based Survey of Atmospheric Science</em>. University of British Columbia.</li>
          <li>Ahrens, C.D. (2012). <em>Meteorology Today: An Introduction to Weather, Climate, and the Environment</em>. Cengage Learning.</li>
          <li>World Meteorological Organization (2018). <em>Guide to Meteorological Instruments and Methods of Observation</em> (WMO-No. 8).</li>
          <li>Stull, R. (2011). Wet-bulb temperature from relative humidity and air temperature. <em>Journal of Applied Meteorology and Climatology</em>, 50(11), 2267-2269.</li>
          <li>Clausius, R. (1850). Über die bewegende Kraft der Wärme. <em>Annalen der Physik</em>, 155(3), 368-397.</li>
        </ul>
      </section>
    </div>
  );
}

export default LearnPage;