import React from 'react';
import { NavLink } from 'react-router-dom';
import {
    ArrowUpOnSquareIcon,
    ArrowPathIcon,
    CheckCircleIcon,
    ExclamationTriangleIcon,
    CircleStackIcon,
    ChartBarIcon
} from '@heroicons/react/24/outline';

const IntelligenceInsights = () => {
    return (
        <div className="flex bg-white h-full -m-6">
            {/* Local Sidebar for Document Analysis */}
            <div className="w-64 border-r border-slate-100 p-6 flex-shrink-0">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mb-1">Case #9421-B</div>
                <h2 className="text-sm font-bold text-slate-900 mb-8 uppercase tracking-tight">TECH MERGER ANALYSIS</h2>

                <div className="space-y-1">
                    <NavLink to="/" className="flex items-center space-x-3 px-3 py-2 text-sm font-medium text-slate-500 hover:bg-slate-50 rounded-md cursor-pointer">
                        <Squares2X2Icon className="h-5 w-5" />
                        <span>Overview</span>
                    </NavLink>
                    <div className="flex items-center space-x-3 px-3 py-2 text-sm font-medium text-red-700 bg-red-50 rounded-md cursor-pointer border-r-2 border-red-700">
                        <div className="w-5 h-5 bg-red-100 rounded-full flex items-center justify-center">
                            <div className="w-2 h-2 bg-red-800 rounded-full"></div>
                        </div>
                        <span>Intelligence Layer</span>
                    </div>
                    <div className="flex items-center space-x-3 px-3 py-2 text-sm font-medium text-slate-500 hover:bg-slate-50 rounded-md cursor-pointer">
                        <DocumentTextIcon className="h-5 w-5" />
                        <span>Document Vault</span>
                    </div>
                    <div className="flex items-center space-x-3 px-3 py-2 text-sm font-medium text-slate-500 hover:bg-slate-50 rounded-md cursor-pointer">
                        <ArrowPathIcon className="h-5 w-5" />
                        <span>Event Timeline</span>
                    </div>
                    <NavLink to="/comparison" className="flex items-center space-x-3 px-3 py-2 text-sm font-medium text-slate-500 hover:bg-slate-50 rounded-md cursor-pointer">
                        <ScaleIcon className="h-5 w-5" />
                        <span>Legal Precedents</span>
                    </NavLink>
                </div>

                <div className="mt-auto pt-80">
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-[10px] font-bold text-slate-400">Analysis Capacity</span>
                        </div>
                        <div className="h-1.5 w-full bg-slate-200 rounded-full overflow-hidden">
                            <div className="h-full bg-red-800 rounded-full" style={{ width: '78%' }}></div>
                        </div>
                        <span className="text-[10px] font-bold text-red-800 mt-2 block">78% AI Tokens Used</span>
                    </div>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-grow p-8 bg-slate-50/50 overflow-y-auto flex">
                <div className="flex-grow pr-8">
                    <div className="flex justify-between items-start mb-6">
                        <div className="space-y-4">
                            <div className="flex items-center space-x-2">
                                <span className="text-[10px] bg-green-100 text-green-700 font-bold px-2 py-0.5 rounded uppercase">ACTIVE</span>
                                <span className="text-[10px] bg-red-100 text-red-800 font-bold px-2 py-0.5 rounded uppercase">PRIORITY ALPHA</span>
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold text-slate-900">Intelligence & Insights</h1>
                                <p className="text-xs text-slate-400 mt-1">Last neural sync: 2 mins ago • Engine v4.2-LTS</p>
                            </div>
                        </div>
                        <div className="flex space-x-3">
                            <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50">
                                <ArrowUpOnSquareIcon className="h-4 w-4" />
                                <span>Export Report</span>
                            </button>
                            <button className="flex items-center space-x-2 px-4 py-2 bg-red-800 rounded-lg text-sm font-medium text-white hover:bg-red-900">
                                <ArrowPathIcon className="h-4 w-4" />
                                <span>Re-run AI Analysis</span>
                            </button>
                        </div>
                    </div>

                    {/* Executive Summary Card */}
                    <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-8 mb-8 relative">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center space-x-3">
                                <div className="text-red-800">✦</div>
                                <span className="text-base font-bold text-slate-900">Automated Executive Summary</span>
                            </div>
                            <div className="text-[10px] font-bold text-slate-400 uppercase">Confidence: 94.2%</div>
                        </div>

                        <p className="text-sm text-slate-600 leading-loose mb-6">
                            The current litigation shows a <span className="text-red-700 font-bold">78% alignment</span> with the 2019 Henderson v. Smith precedent. Our NLP engine has flagged three critical anomalies in the merger disclosure documents that correlate with historical settlement triggers.
                        </p>

                        <ul className="space-y-4 mb-8">
                            {[
                                "Key risks include a compressed merger timeline and potential contractual breach signals identified in Section 4.2 of the disclosure documents.",
                                "Overall case sentiment is cautious but stable, with a 12% increase in favorability following the recent discovery phase.",
                                "Foundational liability remains within projected parameters, though a \"Force Majeure\" clause in Appendix C requires immediate legal scrutiny."
                            ].map((item, i) => (
                                <li key={i} className="flex items-start space-x-3">
                                    <CheckCircleIcon className="h-5 w-5 text-red-700 mt-0.5 flex-shrink-0" />
                                    <span className="text-sm text-slate-600">{item}</span>
                                </li>
                            ))}
                        </ul>

                        <div className="bg-red-50 border border-red-100 p-4 rounded-xl flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                                <div className="w-10 h-10 bg-red-800 rounded-lg flex items-center justify-center text-white">
                                    <ExclamationTriangleIcon className="h-6 w-6" />
                                </div>
                                <div>
                                    <div className="text-xs font-bold text-red-800">Critical Signal Extracted</div>
                                    <div className="text-xs text-slate-500">Unexpected debt obligation discovered in unindexed PDF.</div>
                                </div>
                            </div>
                            <button className="text-xs font-bold text-red-800 hover:underline">Review Source</button>
                        </div>
                    </div>

                    {/* Extracted Signals Grid */}
                    <h3 className="text-sm font-bold text-slate-900 mb-4">Extracted Signals</h3>
                    <div className="grid grid-cols-2 gap-6">
                        <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm">
                            <div className="flex justify-between items-start mb-4">
                                <div className="w-10 h-10 bg-red-50 rounded-lg flex items-center justify-center text-red-800">
                                    <ExclamationTriangleIcon className="h-6 w-6" />
                                </div>
                                <span className="text-[10px] bg-red-50 text-red-800 font-bold px-2 py-0.5 rounded uppercase">HIGH RISK</span>
                            </div>
                            <h4 className="text-sm font-bold text-slate-900 mb-2">Contractual Breach Signal</h4>
                            <p className="text-xs text-slate-500 mb-6 leading-relaxed">
                                Detected in Exhibit B, Page 144. Discrepancy in termination fees exceeds 15% threshold.
                            </p>
                            <div className="flex justify-between items-center text-[10px] font-bold text-slate-400">
                                <span>Source: Doc_921_MergerAgmt.pdf</span>
                                <span className="text-xl">›</span>
                            </div>
                        </div>

                        <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm">
                            <div className="flex justify-between items-start mb-4">
                                <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center text-blue-800">
                                    <CircleStackIcon className="h-6 w-6" />
                                </div>
                                <span className="text-[10px] bg-blue-50 text-blue-800 font-bold px-2 py-0.5 rounded uppercase">FINANCIAL</span>
                            </div>
                            <h4 className="text-sm font-bold text-slate-900 mb-2">Hidden Asset Alignment</h4>
                            <p className="text-xs text-slate-500 mb-6 leading-relaxed">
                                AI matched offshore accounts to secondary subsidiary entities previously undisclosed.
                            </p>
                            <div className="flex justify-between items-center text-[10px] font-bold text-slate-400">
                                <span>Source: EntityMap_v2.xlsx</span>
                                <span className="text-xl">›</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Sidebar Widgets */}
                <div className="w-80 space-y-6">
                    <div className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-sm font-bold text-slate-900">Top Related Precedents</h3>
                            <div className="w-4 h-4 bg-slate-100 rounded-full flex items-center justify-center text-[10px] text-slate-400">i</div>
                        </div>
                        <div className="space-y-6">
                            {[
                                { name: "Henderson v. Smith", match: 89, tags: "Tech Acquisition, Intellectual Property, 2019" },
                                { name: "Orbital Dynamics vs. SEC", match: 74, tags: "Merger Regulation, Disclosure Breach, 2021" },
                                { name: "Zephyr-X Liability Case", match: 62, tags: "Corporate Governance, Fraud Discovery, 2018" }
                            ].map((item, i) => (
                                <div key={i}>
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-sm font-bold text-slate-900">{item.name}</span>
                                        <span className="text-xs font-bold text-red-700">{item.match}%</span>
                                    </div>
                                    <div className="h-1 bg-slate-100 rounded-full overflow-hidden mb-2">
                                        <div className="h-full bg-red-700" style={{ width: `${item.match}%` }}></div>
                                    </div>
                                    <div className="text-[10px] text-slate-400">{item.tags}</div>
                                </div>
                            ))}
                        </div>
                        <button className="w-full text-center text-xs font-bold text-slate-400 mt-8 border-t border-slate-50 pt-4 hover:underline">View All Related Cases ↗</button>
                    </div>

                    <div className="bg-red-800 rounded-xl p-6 text-white relative shadow-lg">
                        <div className="flex items-center space-x-3 mb-6">
                            <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
                                <CheckCircleIcon className="h-5 w-5" />
                            </div>
                            <h3 className="text-sm font-bold">Neural Engine Health</h3>
                        </div>
                        <div className="space-y-4">
                            {[
                                { label: "Textual Reasoning", value: "High (98%)" },
                                { label: "Precedent Matching", value: "Optimal (82%)" },
                                { label: "Entity Extraction", value: "Good (75%)" }
                            ].map((item, i) => (
                                <div key={i}>
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="text-xs text-white/70">{item.label}</span>
                                        <span className="text-xs font-bold">{item.value}</span>
                                    </div>
                                    <div className="h-1 bg-white/20 rounded-full overflow-hidden">
                                        <div className="h-full bg-white rounded-full" style={{ width: '80%' }}></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-white border border-slate-100 rounded-xl p-6 shadow-sm">
                        <h3 className="text-sm font-bold text-slate-900 mb-6">Recent Intel Actions</h3>
                        <div className="space-y-6 relative">
                            <div className="absolute left-1.5 top-1.5 bottom-1.5 w-0.5 bg-slate-100"></div>
                            {[
                                { title: "New Precedent Synced", time: "Today, 10:42 AM", status: "active" },
                                { title: "PDF Discovery OCR Finished", time: "Yesterday, 4:15 PM" },
                                { title: "Initial Case Ingestion", time: "Oct 12, 2023" }
                            ].map((item, i) => (
                                <div key={i} className="flex items-start space-x-4 relative">
                                    <div className={`w-3 h-3 rounded-full mt-1 z-10 ${item.status === 'active' ? 'bg-red-800 ring-4 ring-red-50' : 'bg-slate-200'}`}></div>
                                    <div>
                                        <div className="text-xs font-bold text-slate-900">{item.title}</div>
                                        <div className="text-[10px] text-slate-400">{item.time}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Icons needed for sidebar mapping
const Squares2X2Icon = (props) => <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>;
const DocumentTextIcon = (props) => <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>;
const ScaleIcon = (props) => <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" /></svg>;

export default IntelligenceInsights;
