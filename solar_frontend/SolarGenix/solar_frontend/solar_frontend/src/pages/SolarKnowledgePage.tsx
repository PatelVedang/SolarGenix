import { useState } from "react";

// ── Accordion Item ──────────────────────────────────────────────
const AccordionItem = ({ title, children }: { title: string; children: React.ReactNode }) => {
    const [open, setOpen] = useState(false);
    return (
        <div className="border border-slate-700/60 rounded-xl overflow-hidden mb-3 transition-all duration-200">
            <button
                onClick={() => setOpen(!open)}
                className="w-full flex items-center justify-between px-5 py-4 text-left text-slate-200 hover:bg-slate-800/60 transition-colors"
            >
                <span className="font-medium text-sm md:text-base">{title}</span>
                <svg
                    className={`w-5 h-5 text-amber-400 transition-transform duration-300 ${open ? "rotate-180" : ""}`}
                    fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            {open && (
                <div className="px-5 pb-5 text-slate-400 text-sm leading-relaxed animate-fadeIn">
                    {children}
                </div>
            )}
        </div>
    );
};

// ── Section Card ────────────────────────────────────────────────
const SectionCard = ({ icon, number, title, children }: { icon: string; number: number; title: string; children: React.ReactNode }) => (
    <section className="bg-slate-900/70 border border-slate-700/40 rounded-2xl p-6 md:p-8 backdrop-blur-sm">
        <div className="flex items-center gap-3 mb-6">
            <span className="text-3xl">{icon}</span>
            <div>
                <span className="text-amber-500 text-xs font-bold tracking-widest uppercase">Topic {number}</span>
                <h2 className="text-xl md:text-2xl font-bold text-white">{title}</h2>
            </div>
        </div>
        {children}
    </section>
);

// ── Data ────────────────────────────────────────────────────────
const SolarKnowledgePage = () => {
    return (
        <div className="min-h-screen bg-slate-950 text-white">
            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
                .knowledge-page { font-family: 'Outfit', sans-serif; }
                .animate-fadeIn { animation: fadeIn 0.3s ease-out; }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: translateY(0); } }
                .hero-glow { position:absolute; width:600px; height:600px; background:radial-gradient(circle,rgba(251,191,36,0.08) 0%,transparent 70%); pointer-events:none; }
            `}</style>

            <div className="knowledge-page">
                {/* Hero */}
                <div className="relative overflow-hidden border-b border-slate-800">
                    <div className="hero-glow -top-64 -left-64"></div>
                    <div className="hero-glow -bottom-64 -right-64"></div>
                    <div className="max-w-5xl mx-auto px-4 py-16 md:py-24 text-center relative z-10">
                        <div className="text-6xl mb-4">☀️</div>
                        <h1 className="text-4xl md:text-5xl font-extrabold mb-4">
                            Solar <span className="bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">Knowledge Hub</span>
                        </h1>
                        <p className="text-slate-400 max-w-2xl mx-auto text-lg">
                            Everything you need to know about solar energy — from basics to installation, costs, government schemes, and common myths.
                        </p>
                    </div>
                </div>

                {/* Content */}
                <div className="max-w-4xl mx-auto px-4 py-12 space-y-10">

                    {/* ─── 1. Introduction ──────────────────────────── */}
                    <SectionCard icon="🌞" number={1} title="Introduction to Solar Energy">
                        <AccordionItem title="What is Solar Energy?">
                            <p>Solar energy is the radiant light and heat emitted by the Sun, harnessed using a range of ever-evolving technologies such as photovoltaic (PV) panels, solar thermal collectors, and concentrated solar power (CSP) systems.</p>
                            <p className="mt-2">The Sun radiates approximately 3.8 × 10²⁶ watts of energy every second. Even the tiny fraction that reaches Earth — about 1,370 watts per square metre at the top of the atmosphere — is enough to power all of human civilisation thousands of times over. Solar energy is free, abundant, and available on every continent.</p>
                        </AccordionItem>
                        <AccordionItem title="How Do Solar Panels Work?">
                            <p>Solar panels (photovoltaic modules) are made of semiconductor cells — most commonly crystalline silicon. When sunlight photons hit a cell, they knock electrons loose from their atoms. The cell's internal electric field pushes those free electrons in one direction, creating a flow of direct current (DC) electricity.</p>
                            <ul className="list-disc ml-5 mt-2 space-y-1">
                                <li><strong>Photons hit the cell</strong> — sunlight energy is absorbed by the silicon wafer.</li>
                                <li><strong>Electrons are freed</strong> — the photovoltaic effect creates electron-hole pairs.</li>
                                <li><strong>Current flows</strong> — an internal electric field drives electrons through an external circuit.</li>
                                <li><strong>Inverter converts DC → AC</strong> — the DC output is converted to alternating current (AC) for household use.</li>
                            </ul>
                        </AccordionItem>
                        <AccordionItem title="Why is Solar Energy Important?">
                            <p>Solar energy is one of the most sustainable and cleanest forms of energy available today. Here's why it matters:</p>
                            <ul className="list-disc ml-5 mt-2 space-y-1">
                                <li><strong>Inexhaustible source</strong> — the Sun will continue to shine for another ~5 billion years.</li>
                                <li><strong>Zero emissions</strong> — solar panels produce electricity without burning fossil fuels or emitting greenhouse gases.</li>
                                <li><strong>Decentralised power</strong> — anyone with a rooftop can generate their own electricity, reducing dependence on centralised grids.</li>
                                <li><strong>Falling costs</strong> — the cost of solar panels has dropped by over 90 % in the last decade, making it one of the cheapest sources of new electricity in most countries.</li>
                                <li><strong>Job creation</strong> — the solar industry is one of the fastest-growing job sectors globally.</li>
                            </ul>
                        </AccordionItem>
                        <AccordionItem title="How Solar Panels Generate Electricity">
                            <p>The complete journey from sunlight to usable electricity involves these stages:</p>
                            <ol className="list-decimal ml-5 mt-2 space-y-1">
                                <li><strong>Light absorption</strong> — silicon cells absorb photons from sunlight.</li>
                                <li><strong>Electron excitation</strong> — absorbed energy frees electrons, creating electron-hole pairs (the photovoltaic effect).</li>
                                <li><strong>DC generation</strong> — the built-in electric field across the p-n junction pushes electrons, creating direct current.</li>
                                <li><strong>Inversion</strong> — a solar inverter converts DC into 230 V AC power compatible with home appliances.</li>
                                <li><strong>Grid connection / consumption</strong> — electricity is consumed on-site or exported to the grid through a net meter.</li>
                            </ol>
                        </AccordionItem>
                    </SectionCard>

                    {/* ─── 2. Benefits ──────────────────────────────── */}
                    <SectionCard icon="✅" number={2} title="Benefits of Installing Solar Panels">
                        <AccordionItem title="Reduced Electricity Bills">
                            <p>Installing solar panels can cut your monthly electricity bill by 50–90 %, depending on system size, your consumption pattern, and local sunlight hours. Any excess energy generated can often be exported to the grid, earning you credits through net metering — effectively running your meter backwards.</p>
                            <p className="mt-2">For a typical Indian household consuming ~300 units/month, a 3 kW rooftop system can offset the majority of that usage, saving ₹1,500–₹2,500 per month.</p>
                        </AccordionItem>
                        <AccordionItem title="Renewable & Clean Energy Source">
                            <p>Unlike coal or natural gas, solar energy is completely renewable. The Sun delivers more energy to Earth in one hour than all of humanity uses in an entire year. By switching to solar, you're tapping into an unlimited resource with zero fuel costs, no supply-chain disruptions, and no price volatility.</p>
                        </AccordionItem>
                        <AccordionItem title="Environmental Benefits">
                            <p>Every kilowatt-hour of solar electricity avoids approximately 0.7–1.0 kg of CO₂ emissions compared to coal-fired power. A typical 5 kW residential system offsets roughly 5–7 tonnes of CO₂ per year — equivalent to planting over 200 trees annually.</p>
                            <p className="mt-2">Solar power also reduces water consumption (thermal power plants use massive amounts of water for cooling), air pollution, and dependence on imported fossil fuels.</p>
                        </AccordionItem>
                        <AccordionItem title="Government Incentives & Subsidies">
                            <p>Many governments worldwide offer generous incentives for solar adoption:</p>
                            <ul className="list-disc ml-5 mt-2 space-y-1">
                                <li><strong>India</strong> — the PM Surya Ghar Muft Bijli Yojana provides up to ₹78,000 subsidy for residential rooftop systems.</li>
                                <li><strong>Net metering</strong> — sell excess power back to the grid at favourable rates.</li>
                                <li><strong>Tax benefits</strong> — accelerated depreciation benefits for commercial installations.</li>
                                <li><strong>State-level incentives</strong> — additional subsidies and rebates vary by state/region.</li>
                            </ul>
                        </AccordionItem>
                        <AccordionItem title="Increased Property Value">
                            <p>Homes with solar panel installations have been shown to sell for 3–4 % more on average compared to similar homes without solar. Buyers value the long-term savings and environmental credentials, making solar a smart investment that pays for itself and adds tangible real-estate value.</p>
                        </AccordionItem>
                        <AccordionItem title="Energy Independence">
                            <p>With solar panels (and optionally battery storage), you can significantly reduce your reliance on the utility grid. This protects you from rising electricity tariffs, power cuts, and supply disruptions. In rural or off-grid areas, solar can provide reliable electricity where grid access is limited or unreliable.</p>
                        </AccordionItem>
                    </SectionCard>

                    {/* ─── 3. Should You Install? ─────────────────── */}
                    <SectionCard icon="🤔" number={3} title="Should You Install Solar?">
                        <AccordionItem title="Average Monthly Electricity Bill">
                            <p>If your monthly electricity bill exceeds ₹1,500–₹2,000 (or your local equivalent), solar becomes financially attractive. Higher bills mean more savings — the ROI improves dramatically for bills above ₹3,000/month.</p>
                        </AccordionItem>
                        <AccordionItem title="Roof Size & Direction">
                            <p>You need approximately 60–80 sq ft of shadow-free roof area per kW of panels. South-facing roofs (in the Northern Hemisphere) receive the most sunlight. East- and west-facing roofs also work well, typically producing 80–90 % of the output of a south-facing installation.</p>
                        </AccordionItem>
                        <AccordionItem title="Location & Sunlight Availability">
                            <p>India receives 4–7 kWh/m²/day of solar irradiance — among the highest in the world. Even states with moderate sunlight (e.g., Kerala, Northeast) receive enough for solar to be viable. Check your area's peak sun hours; 4+ hours/day is sufficient for a good return.</p>
                        </AccordionItem>
                        <AccordionItem title="Electricity Consumption Pattern">
                            <p>Solar works best when consumption overlaps with generation hours (daytime). If most of your usage is during the day (air conditioning, appliances), you'll maximise self-consumption. For nighttime-heavy usage, battery storage or net metering compensates effectively.</p>
                        </AccordionItem>
                        <AccordionItem title="Budget & ROI">
                            <p>A residential rooftop system typically costs ₹50,000–₹70,000 per kW (after subsidy). The payback period is usually 3–5 years, after which electricity is essentially free for the remaining 20+ years of the system's life. That's an effective annual return of 20–30 % — far better than most financial investments.</p>
                        </AccordionItem>
                        <AccordionItem title="Quick Solar Suitability Checklist">
                            <div className="space-y-2">
                                <div className="flex items-center gap-2"><span className="text-green-400">✔</span> Roof receives direct sunlight for ≥ 5 hours/day</div>
                                <div className="flex items-center gap-2"><span className="text-green-400">✔</span> Monthly electricity bill is ≥ ₹1,500</div>
                                <div className="flex items-center gap-2"><span className="text-green-400">✔</span> Shadow-free roof area of at least 100 sq ft available</div>
                                <div className="flex items-center gap-2"><span className="text-green-400">✔</span> Roof is structurally sound and less than 20 years old</div>
                                <div className="flex items-center gap-2"><span className="text-green-400">✔</span> No major obstructions (trees, tall buildings) blocking sunlight</div>
                                <p className="mt-3 text-amber-400 font-medium">If you checked 3 or more, solar is likely a great fit for you!</p>
                            </div>
                        </AccordionItem>
                    </SectionCard>

                    {/* ─── 4. Cost ──────────────────────────────────── */}
                    <SectionCard icon="💰" number={4} title="Cost of Solar Installation">
                        <AccordionItem title="Panel Cost">
                            <p>Solar panels cost approximately ₹25,000–₹35,000 per kW for standard polycrystalline modules and ₹30,000–₹45,000 per kW for high-efficiency monocrystalline modules. Premium bifacial panels can cost more but generate 5–15 % additional energy from reflected light.</p>
                        </AccordionItem>
                        <AccordionItem title="Installation Cost">
                            <p>Installation typically adds ₹15,000–₹25,000 per kW, covering mounting structures, wiring, inverter, earthing, and labour. A complete 3 kW on-grid system (panels + installation + inverter) averages ₹1.8–₹2.5 lakh before subsidies, and ₹1.0–₹1.7 lakh after government subsidy.</p>
                        </AccordionItem>
                        <AccordionItem title="Maintenance Cost">
                            <p>Solar panels have minimal maintenance requirements. Annual costs are typically ₹1,000–₹3,000 for periodic cleaning and inspection. Inverters may need replacement once in 10–12 years (₹15,000–₹30,000). There are no moving parts, so wear-and-tear costs are negligible.</p>
                        </AccordionItem>
                        <AccordionItem title="Payback Period">
                            <p>Most residential systems pay for themselves in <strong>3–5 years</strong>, depending on system size, electricity tariff, and local sunlight. After payback, you enjoy 20+ years of essentially free electricity. Commercial systems with accelerated depreciation benefits often achieve payback in 2–3 years.</p>
                        </AccordionItem>
                        <AccordionItem title="Return on Investment (ROI)">
                            <p>Over a 25-year lifespan, a well-designed solar system delivers total savings of 3–5× the initial investment. The effective annual ROI is 20–30 %, far outperforming fixed deposits (6–7 %), mutual funds (12–15 %), and even real estate in many cases. Solar is one of the safest, highest-return investments available to homeowners.</p>
                        </AccordionItem>
                    </SectionCard>

                    {/* ─── 5. Types of Systems ─────────────────────── */}
                    <SectionCard icon="🔌" number={5} title="Types of Solar Systems">
                        <AccordionItem title="On-Grid (Grid-Tied) System">
                            <p>The most common and affordable type. On-grid systems are directly connected to the utility grid. Excess energy is exported to the grid (earning credits via net metering), and you draw from the grid when solar production is insufficient (e.g., at night).</p>
                            <ul className="list-disc ml-5 mt-2 space-y-1">
                                <li><strong>Pros:</strong> Lowest cost, no battery required, net metering savings.</li>
                                <li><strong>Cons:</strong> No power during grid outages (for safety reasons, the inverter shuts off).</li>
                                <li><strong>Best for:</strong> Urban homes with reliable grid supply and high electricity bills.</li>
                            </ul>
                        </AccordionItem>
                        <AccordionItem title="Off-Grid System">
                            <p>Completely independent of the utility grid. Off-grid systems use battery banks to store energy for use when the sun isn't shining. They require careful sizing to ensure reliable power 24/7.</p>
                            <ul className="list-disc ml-5 mt-2 space-y-1">
                                <li><strong>Pros:</strong> Full energy independence, works in remote locations.</li>
                                <li><strong>Cons:</strong> Higher cost (batteries are expensive), requires more maintenance, limited capacity.</li>
                                <li><strong>Best for:</strong> Rural areas, farmhouses, remote locations without grid access.</li>
                            </ul>
                        </AccordionItem>
                        <AccordionItem title="Hybrid Solar System">
                            <p>Combines the best of both worlds — connected to the grid <em>and</em> equipped with battery storage. During the day, solar powers your home and charges the battery. At night or during outages, the battery takes over. Excess energy can still be exported to the grid.</p>
                            <ul className="list-disc ml-5 mt-2 space-y-1">
                                <li><strong>Pros:</strong> Power backup during outages, grid export, maximum self-consumption.</li>
                                <li><strong>Cons:</strong> Highest upfront cost.</li>
                                <li><strong>Best for:</strong> Areas with frequent power cuts, users who want both savings and backup.</li>
                            </ul>
                        </AccordionItem>
                    </SectionCard>

                    {/* ─── 6. Types of Panels ─────────────────────── */}
                    <SectionCard icon="🔬" number={6} title="Types of Solar Panels">
                        <AccordionItem title="Monocrystalline Panels">
                            <p>Made from a single crystal of silicon, these panels are the most efficient and space-efficient option available.</p>
                            <div className="mt-3 grid grid-cols-3 gap-3 text-center">
                                <div className="bg-slate-800 rounded-lg p-3"><div className="text-amber-400 font-bold">20–24%</div><div className="text-xs text-slate-500">Efficiency</div></div>
                                <div className="bg-slate-800 rounded-lg p-3"><div className="text-amber-400 font-bold">₹30–45k</div><div className="text-xs text-slate-500">Per kW</div></div>
                                <div className="bg-slate-800 rounded-lg p-3"><div className="text-amber-400 font-bold">25–30 yr</div><div className="text-xs text-slate-500">Lifespan</div></div>
                            </div>
                        </AccordionItem>
                        <AccordionItem title="Polycrystalline Panels">
                            <p>Made from multiple silicon crystals melted together. Slightly less efficient but more affordable, making them popular for budget-conscious installations.</p>
                            <div className="mt-3 grid grid-cols-3 gap-3 text-center">
                                <div className="bg-slate-800 rounded-lg p-3"><div className="text-amber-400 font-bold">15–18%</div><div className="text-xs text-slate-500">Efficiency</div></div>
                                <div className="bg-slate-800 rounded-lg p-3"><div className="text-amber-400 font-bold">₹25–35k</div><div className="text-xs text-slate-500">Per kW</div></div>
                                <div className="bg-slate-800 rounded-lg p-3"><div className="text-amber-400 font-bold">25 yr</div><div className="text-xs text-slate-500">Lifespan</div></div>
                            </div>
                        </AccordionItem>
                        <AccordionItem title="Thin-Film Panels">
                            <p>Made by depositing a thin layer of photovoltaic material (e.g., CdTe, amorphous silicon) on a substrate. Flexible, lightweight, and perform slightly better in low-light or high-temperature conditions.</p>
                            <div className="mt-3 grid grid-cols-3 gap-3 text-center">
                                <div className="bg-slate-800 rounded-lg p-3"><div className="text-amber-400 font-bold">10–13%</div><div className="text-xs text-slate-500">Efficiency</div></div>
                                <div className="bg-slate-800 rounded-lg p-3"><div className="text-amber-400 font-bold">₹20–30k</div><div className="text-xs text-slate-500">Per kW</div></div>
                                <div className="bg-slate-800 rounded-lg p-3"><div className="text-amber-400 font-bold">15–20 yr</div><div className="text-xs text-slate-500">Lifespan</div></div>
                            </div>
                        </AccordionItem>
                    </SectionCard>

                    {/* ─── 7. Maintenance ─────────────────────────── */}
                    <SectionCard icon="🔧" number={7} title="Maintenance of Solar Panels">
                        <AccordionItem title="Cleaning Panels">
                            <p>Dust, bird droppings, and pollen can reduce output by 5–25 %. Clean panels with water and a soft brush or sponge every 2–4 weeks. Avoid abrasive cleaners or high-pressure jets. In dusty areas, automatic cleaning systems or nano-coatings can help. Early morning cleaning (when panels are cool and dew-covered) is most effective.</p>
                        </AccordionItem>
                        <AccordionItem title="Checking Wiring & Connections">
                            <p>Inspect wiring, connectors, and junction boxes every 6 months for signs of wear, corrosion, or loose connections. Rodents can chew through cables — use conduit protection in areas prone to pests. Ensure earthing connections are intact for safety.</p>
                        </AccordionItem>
                        <AccordionItem title="Inverter Maintenance">
                            <p>Inverters are the most active component and need periodic attention. Check indicator lights and error codes regularly. Keep the inverter in a well-ventilated, shaded area to prevent overheating. String inverters typically last 10–12 years; micro-inverters can last 20+ years. Budget for one inverter replacement during the panel lifetime.</p>
                        </AccordionItem>
                        <AccordionItem title="Monitoring Energy Output">
                            <p>Use your inverter's app or monitoring portal to track daily, monthly, and yearly production. A sudden drop in output could indicate panel soiling, shading from new construction, or an electrical fault. Many modern systems send automatic alerts when performance drops below expected levels.</p>
                        </AccordionItem>
                        <AccordionItem title="Professional Inspection">
                            <p>Schedule a professional inspection at least once a year. A certified technician will check panel integrity, wiring, inverter performance, mounting structure, and overall system health. Annual maintenance contracts typically cost ₹2,000–₹5,000 and can catch issues before they become expensive problems.</p>
                        </AccordionItem>
                    </SectionCard>

                    {/* ─── 8. Lifespan ─────────────────────────────── */}
                    <SectionCard icon="⏳" number={8} title="Lifespan of Solar Panels">
                        <AccordionItem title="Typical Lifespan (25–30 Years)">
                            <p>Modern solar panels are engineered to last 25–30 years or more. Many panels installed in the 1980s and 1990s are still producing electricity today. The panels don't suddenly stop working after 25 years — they continue generating power, just at a slightly reduced efficiency.</p>
                        </AccordionItem>
                        <AccordionItem title="Panel Degradation Rate">
                            <p>Solar panels degrade at approximately 0.3–0.8 % per year. This means after 25 years, a panel will still produce about 80–87 % of its original rated capacity. Premium manufacturers like LG, SunPower, and Longi guarantee degradation rates as low as 0.25 % per year.</p>
                            <div className="mt-3 bg-slate-800 rounded-lg p-4">
                                <div className="text-xs text-slate-500 mb-2">Example Degradation Timeline (0.5%/year)</div>
                                <div className="flex justify-between text-sm">
                                    <div><span className="text-amber-400 font-bold">Year 1:</span> 100%</div>
                                    <div><span className="text-amber-400 font-bold">Year 10:</span> ~95%</div>
                                    <div><span className="text-amber-400 font-bold">Year 25:</span> ~87.5%</div>
                                </div>
                            </div>
                        </AccordionItem>
                        <AccordionItem title="Warranty Information">
                            <p>Most solar panels come with two types of warranties:</p>
                            <ul className="list-disc ml-5 mt-2 space-y-1">
                                <li><strong>Product warranty</strong> — covers manufacturing defects, typically 10–12 years, sometimes 25 years for premium brands.</li>
                                <li><strong>Performance warranty</strong> — guarantees that the panel will produce at least 80–90 % of its rated output after 25 years.</li>
                                <li><strong>Inverter warranty</strong> — typically 5–10 years, extendable to 15–25 years with premium brands.</li>
                            </ul>
                        </AccordionItem>
                    </SectionCard>

                    {/* ─── 9. Government Subsidies ─────────────────── */}
                    <SectionCard icon="🏛️" number={9} title="Government Subsidies & Incentives">
                        <AccordionItem title="Government Solar Schemes">
                            <p>The Indian Government's <strong>PM Surya Ghar Muft Bijli Yojana</strong> (launched 2024) aims to install rooftop solar on 1 crore households, providing up to 300 units of free electricity per month. Key benefits:</p>
                            <ul className="list-disc ml-5 mt-2 space-y-1">
                                <li>Subsidy of ₹30,000 for 1 kW systems</li>
                                <li>Subsidy of ₹60,000 for 2 kW systems</li>
                                <li>Subsidy of ₹78,000 for 3 kW and above systems</li>
                                <li>Direct Benefit Transfer (DBT) to your bank account after installation</li>
                            </ul>
                        </AccordionItem>
                        <AccordionItem title="Net Metering">
                            <p>Net metering allows you to export excess solar electricity to the grid and receive credits on your bill. Your meter runs backwards when you export, and forwards when you consume from the grid. At the end of the billing cycle, you only pay for the <em>net</em> energy consumed.</p>
                            <p className="mt-2">Net metering policies vary by state. Most states allow systems up to the sanctioned load (typically 1–10 kW for residential). Some states offer feed-in tariffs where you're paid a fixed rate for exported energy.</p>
                        </AccordionItem>
                        <AccordionItem title="Tax Benefits">
                            <p>Commercial and industrial solar installations in India can claim <strong>40 % accelerated depreciation</strong> in the first year, significantly reducing taxable income. Residential users benefit indirectly through reduced electricity costs (which are not taxed as income). GST on solar panels and related equipment is currently at 12 %.</p>
                        </AccordionItem>
                        <AccordionItem title="Subsidy Programs by State">
                            <p>Several states offer additional incentives on top of central subsidies:</p>
                            <ul className="list-disc ml-5 mt-2 space-y-1">
                                <li><strong>Gujarat</strong> — additional state subsidy + favourable net metering</li>
                                <li><strong>Maharashtra</strong> — MEDA subsidies for residential and agricultural solar</li>
                                <li><strong>Karnataka</strong> — BESCOM net metering with competitive feed-in tariff</li>
                                <li><strong>Delhi</strong> — generation-based incentive (GBI) of ₹2/unit for surplus power</li>
                                <li><strong>Rajasthan</strong> — strong solar irradiance + state incentives for large installations</li>
                            </ul>
                        </AccordionItem>
                    </SectionCard>

                    {/* ─── 10. Environmental Impact ─────────────────── */}
                    <SectionCard icon="🌍" number={10} title="Environmental Impact">
                        <AccordionItem title="Carbon Emission Reduction">
                            <p>Every kWh of solar replaces grid electricity that is largely coal-based in India. A 5 kW residential system avoids approximately <strong>5–7 tonnes of CO₂ per year</strong>. Over 25 years, that's 125–175 tonnes of CO₂ kept out of the atmosphere — equivalent to taking 3–4 cars off the road permanently.</p>
                        </AccordionItem>
                        <AccordionItem title="Reduced Fossil Fuel Usage">
                            <p>India currently generates over 70 % of its electricity from fossil fuels (primarily coal). By adopting solar, you directly reduce demand for coal mining, transportation, and combustion. Each kW of solar installed displaces approximately 1.5 tonnes of coal per year.</p>
                        </AccordionItem>
                        <AccordionItem title="Contribution to Green Energy Goals">
                            <p>India has committed to <strong>500 GW of non-fossil fuel capacity by 2030</strong> and net-zero emissions by 2070. Residential rooftop solar is a critical pillar of this strategy. By installing solar, you're directly contributing to national and global climate goals, helping secure a cleaner future for the next generation.</p>
                        </AccordionItem>
                    </SectionCard>

                    {/* ─── 11. Common Myths ─────────────────────────── */}
                    <SectionCard icon="🚫" number={11} title="Common Myths About Solar Panels">
                        <AccordionItem title="&quot;Solar doesn't work in cloudy weather&quot;">
                            <p><strong>Myth busted:</strong> Solar panels work on <em>light</em>, not heat. They still generate electricity on cloudy days — typically 25–40 % of their peak output. Germany, one of the cloudiest countries in Europe, is among the world's top solar producers. Modern panels are increasingly efficient in diffuse light conditions.</p>
                        </AccordionItem>
                        <AccordionItem title="&quot;Solar panels are too expensive&quot;">
                            <p><strong>Myth busted:</strong> Solar panel prices have dropped by over 90 % in the last decade. With government subsidies, a 3 kW system costs ₹1.0–₹1.7 lakh — comparable to a mid-range smartphone on EMI. The system pays for itself in 3–5 years and then generates free electricity for 20+ more years.</p>
                        </AccordionItem>
                        <AccordionItem title="&quot;Maintenance is difficult and expensive&quot;">
                            <p><strong>Myth busted:</strong> Solar panels have no moving parts. Maintenance is limited to occasional cleaning (every 2–4 weeks) and an annual professional check-up. Total annual maintenance cost is ₹1,000–₹3,000 — less than what most people spend on a single dinner out.</p>
                        </AccordionItem>
                        <AccordionItem title="&quot;Solar panels damage roofs&quot;">
                            <p><strong>Myth busted:</strong> Properly installed solar panels actually <em>protect</em> the covered portion of your roof from sun, rain, and hail damage. Modern mounting systems use non-penetrating clamps or ballasted mounts that don't drill into the roof. Reputable installers provide waterproofing guarantees.</p>
                        </AccordionItem>
                    </SectionCard>

                    {/* ─── 12. Installation Process ─────────────────── */}
                    <SectionCard icon="🏗️" number={12} title="Solar Installation Process">
                        <AccordionItem title="Step 1: Site Assessment">
                            <p>A certified solar engineer visits your property to evaluate roof condition, orientation, shading, structural strength, and available area. They also assess your electrical panel, sanctioned load, and historical electricity consumption to recommend the optimal system size.</p>
                        </AccordionItem>
                        <AccordionItem title="Step 2: System Design">
                            <p>Based on the site assessment, a customised design is prepared including panel layout, inverter sizing, wiring diagram, and mounting structure specifications. The design maximises energy production while complying with local building codes and utility regulations.</p>
                        </AccordionItem>
                        <AccordionItem title="Step 3: Installation">
                            <p>Installation typically takes 1–3 days for residential systems. The process includes:</p>
                            <ol className="list-decimal ml-5 mt-2 space-y-1">
                                <li>Mounting structure installation on the roof</li>
                                <li>Panel placement and secure fastening</li>
                                <li>DC wiring from panels to inverter</li>
                                <li>Inverter installation and AC wiring</li>
                                <li>Earthing and lightning protection</li>
                                <li>Testing and commissioning</li>
                            </ol>
                        </AccordionItem>
                        <AccordionItem title="Step 4: Grid Connection & Net Meter">
                            <p>After installation, your DISCOM (electricity distribution company) inspects the system and installs a bi-directional net meter. This process takes 1–4 weeks depending on your state. Once approved, you can start exporting excess power and earning credits.</p>
                        </AccordionItem>
                        <AccordionItem title="Step 5: Monitoring & Handover">
                            <p>The installer configures remote monitoring (via app or web portal), hands over all documentation (warranties, test reports, user manual), and provides training on basic maintenance. You can now track your system's real-time performance, daily/monthly generation, savings, and carbon offset from your phone.</p>
                        </AccordionItem>
                    </SectionCard>

                    {/* Footer */}
                    <div className="text-center text-slate-600 text-sm pt-8 pb-12">
                        <p>Built with ☀️ by <span className="text-amber-500 font-semibold">SolarGenix</span></p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SolarKnowledgePage;
