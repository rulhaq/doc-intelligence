import React from 'react';
import { NavLink } from 'react-router-dom';
import {
    ArrowUpOnSquareIcon,
    ShareIcon,
    CheckCircleIcon,
    PlusIcon,
    ExclamationCircleIcon
} from '@heroicons/react/24/outline';

const CaseComparison = () => {
    return (
        <div className="flex bg-white h-full -m-6">
            {/* Local Sidebar for Comparison Selection */}
            <div className="w-64 border-r border-slate-100 p-6 flex-shrink-0">
                <h2 className="text-sm font-bold text-slate-900 mb-1">Case Explorer</h2>
                <p className="text-xs text-slate-400 mb-6">Select cases to compare</p>

                <div className="space-y-6">
                    <div className="space-y-1">
                        <NavLink to="/" className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-md cursor-pointer">
                            <div className="w-5 h-5 bg-slate-100 rounded flex items-center justify-center">
                                <div className="w-3 h-3 bg-slate-400 rounded-sm"></div>
                            </div>
                            <span>All Legal Cases</span>
                        </NavLink>
                        <div className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-red-700 bg-red-50 rounded-md cursor-pointer">
                            <div className="w-5 h-5 bg-red-100 rounded flex items-center justify-center">
                                <div className="w-3 h-3 bg-red-800 rounded-sm"></div>
                            </div>
                            <span>Recent Comparisons</span>
                        </div>
                    </div>

                    <div className="pt-4">
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-3">ACTIVE COMPARISON</p>
                        <div className="space-y-2">
                            <div className="border border-red-200 bg-red-50 p-3 rounded-lg relative">
                                <div className="text-[10px] font-bold text-red-800">CASE-8821</div>
                                <div className="text-xs font-medium text-slate-900 truncate">Global Logistics v. Nordic</div>
                                <CheckCircleIcon className="absolute top-2 right-2 h-3 w-3 text-red-800" />
                            </div>
                            <div className="border border-red-200 bg-red-50 p-3 rounded-lg relative">
                                <div className="text-[10px] font-bold text-red-800">CASE-9042</div>
                                <div className="text-xs font-medium text-slate-900 truncate">Atlas Tech IP Dispute</div>
                                <CheckCircleIcon className="absolute top-2 right-2 h-3 w-3 text-red-800" />
                            </div>
                            <button className="w-full border border-dashed border-slate-200 py-3 rounded-lg flex items-center justify-center space-x-2 text-slate-300 hover:bg-slate-50">
                                <PlusIcon className="h-4 w-4" />
                                <span className="text-xs">Add Case C</span>
                            </button>
                        </div>
                    </div>
                </div>

                <div className="mt-auto pt-40">
                    <button className="w-full bg-red-900 text-white py-2 rounded-lg text-xs font-bold flex items-center justify-center space-x-2">
                        <PlusIcon className="h-4 w-4" />
                        <span>New Case Analysis</span>
                    </button>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-grow p-8 bg-slate-50/50 overflow-y-auto">
                <div className="flex justify-between items-start mb-6">
                    <div>
                        <div className="text-xs text-slate-400 flex items-center space-x-1 mb-2">
                            <span>Intelligence</span>
                            <span>/</span>
                            <span className="text-slate-600 font-medium">Case Comparison</span>
                        </div>
                        <h1 className="text-3xl font-bold text-slate-900">Case Comparison & Patterns</h1>
                        <p className="text-sm text-slate-400 mt-1">Advanced semantic analysis across selected legal documents.</p>
                    </div>
                    <div className="flex space-x-3">
                        <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50">
                            <ArrowUpOnSquareIcon className="h-4 w-4" />
                            <span>Export Report</span>
                        </button>
                        <button className="flex items-center space-x-2 px-4 py-2 bg-red-800 rounded-lg text-sm font-medium text-white hover:bg-red-900">
                            <ShareIcon className="h-4 w-4" />
                            <span>Share Insights</span>
                        </button>
                    </div>
                </div>

                {/* Comparison Table */}
                <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden mb-8">
                    <table className="w-full border-collapse">
                        <thead>
                            <tr className="border-b border-slate-100">
                                <th className="w-1/4 p-6 text-left text-[10px] font-bold text-slate-400 uppercase">ATTRIBUTE COMPARISON</th>
                                <th className="w-3/8 p-6 text-left">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-1 h-8 bg-red-800"></div>
                                        <div>
                                            <div className="text-[10px] font-bold text-red-800">CASE A</div>
                                            <div className="text-base font-bold text-slate-900">Global Logistics v. Nordic</div>
                                        </div>
                                    </div>
                                </th>
                                <th className="w-3/8 p-6 text-left">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-1 h-8 bg-red-900"></div>
                                        <div>
                                            <div className="text-[10px] font-bold text-red-800">CASE B</div>
                                            <div className="text-base font-bold text-slate-900">Atlas Tech IP Dispute</div>
                                        </div>
                                    </div>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr className="bg-slate-50/30">
                                <td colSpan="3" className="p-4 px-6 text-[10px] font-bold text-slate-400 uppercase">KEY ATTRIBUTES</td>
                            </tr>
                            <tr className="border-b border-slate-50">
                                <td className="p-6 text-sm font-bold text-slate-600">Jurisdiction</td>
                                <td className="p-6 text-sm text-slate-600">SDNY - Southern District of NY</td>
                                <td className="p-6 text-sm text-slate-600">
                                    <div className="flex items-center justify-between">
                                        <span>Northern District of California</span>
                                        <span className="text-[10px] bg-yellow-100 text-yellow-700 font-bold px-2 py-0.5 rounded uppercase">DIFFERENCE</span>
                                    </div>
                                </td>
                            </tr>
                            <tr className="border-b border-slate-50">
                                <td className="p-6 text-sm font-bold text-slate-600">Core Argument</td>
                                <td className="p-6 text-sm text-slate-600 leading-relaxed">Breach of contract regarding maritime supply chain delays during Q3 2023.</td>
                                <td className="p-6 text-sm text-slate-600 leading-relaxed">Infringement on cloud-native database architecture patents and trade secrets.</td>
                            </tr>
                            <tr className="border-b border-slate-50">
                                <td className="p-6 text-sm font-bold text-slate-600">Financial Impact</td>
                                <td className="p-6 text-sm text-slate-900 font-medium">$12.4M (Estimated)</td>
                                <td className="p-6 text-sm text-slate-900 font-medium">$85.0M (Potential)</td>
                            </tr>
                            <tr className="bg-slate-50/30">
                                <td colSpan="3" className="p-4 px-6 text-[10px] font-bold text-slate-400 uppercase">THEMATIC SIMILARITIES & PATTERNS</td>
                            </tr>
                            <tr className="border-b border-slate-50 bg-red-50/10">
                                <td className="p-6">
                                    <div className="flex items-center space-x-2">
                                        <div className="text-red-800">✦</div>
                                        <span className="text-sm font-bold text-red-800">Shared Pattern</span>
                                    </div>
                                </td>
                                <td colSpan="2" className="p-6">
                                    <div className="flex items-center space-x-3 mb-2">
                                        <span className="text-sm font-bold text-slate-900">Recursive Liability Structure</span>
                                        <span className="text-[10px] bg-red-800 text-white font-bold px-2 py-0.5 rounded uppercase">HIGH SIMILARITY</span>
                                    </div>
                                    <p className="text-sm text-slate-500 leading-relaxed">
                                        Both cases involve a third-party holding company in the Caymans with identical ownership structures. AI identifies a potential 84% probability of corporate veil overlap.
                                    </p>
                                </td>
                            </tr>
                            <tr className="border-b border-slate-50">
                                <td className="p-6 text-sm font-bold text-slate-600">Precedents Cited</td>
                                <td className="p-6">
                                    <div className="flex space-x-2">
                                        <span className="bg-slate-100 px-2 py-1 rounded text-xs text-slate-500">Vandelay v. Industries</span>
                                        <span className="bg-slate-100 px-2 py-1 rounded text-xs text-slate-500">Maritime Law 201(a)</span>
                                    </div>
                                </td>
                                <td className="p-6">
                                    <div className="flex space-x-2">
                                        <span className="bg-slate-100 px-2 py-1 rounded text-xs text-slate-500">Oracle v. Google</span>
                                        <span className="bg-slate-100 px-2 py-1 rounded text-xs text-slate-500">Intellectual Property Stat. 44</span>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td className="p-6 text-sm font-bold text-slate-600">Outcome Probability</td>
                                <td className="p-6">
                                    <div className="flex items-center justify-between mb-1">
                                        <div className="h-1.5 w-48 bg-slate-100 rounded-full overflow-hidden">
                                            <div className="h-full bg-red-800 rounded-full" style={{ width: '65%' }}></div>
                                        </div>
                                        <span className="text-xs font-bold text-slate-900 ml-4">65% Win</span>
                                    </div>
                                </td>
                                <td className="p-6">
                                    <div className="flex items-center justify-between mb-1">
                                        <div className="h-1.5 w-48 bg-slate-100 rounded-full overflow-hidden">
                                            <div className="h-full bg-red-800 rounded-full" style={{ width: '42%' }}></div>
                                        </div>
                                        <span className="text-xs font-bold text-slate-900 ml-4">42% Win</span>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                {/* Metric Cards */}
                <div className="grid grid-cols-3 gap-6">
                    <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm relative overflow-hidden">
                        <div className="flex items-center justify-between mb-6">
                            <div className="w-10 h-10 bg-red-50 rounded-full flex items-center justify-center text-red-800">
                                <div className="grid grid-cols-2 gap-0.5">
                                    <div className="w-1.5 h-1.5 bg-red-800 rounded-full"></div>
                                    <div className="w-1.5 h-1.5 bg-red-800 rounded-full"></div>
                                    <div className="w-1.5 h-1.5 bg-red-800 rounded-full"></div>
                                    <div className="w-1.5 h-1.5 bg-red-800 rounded-full opacity-30"></div>
                                </div>
                            </div>
                            <h3 className="text-sm font-bold text-slate-800 flex-grow ml-4">Thematic Similarity</h3>
                        </div>
                        <p className="text-xs text-slate-500 mb-6 leading-relaxed">
                            Strong correlation found in discovery motions and expert witness profiles between Case A and Case B.
                        </p>
                        <div className="flex justify-between items-end">
                            <span className="text-[10px] font-bold text-slate-400 uppercase">MATCH SCORE</span>
                            <span className="text-xl font-bold text-slate-900 tracking-tight">72%</span>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm">
                        <div className="flex items-center justify-between mb-6">
                            <div className="w-10 h-10 bg-red-50 rounded-full flex items-center justify-center text-red-800">
                                <ExclamationCircleIcon className="h-6 w-6" />
                            </div>
                            <h3 className="text-sm font-bold text-slate-800 flex-grow ml-4">Pattern Analysis</h3>
                        </div>
                        <p className="text-xs text-slate-500 mb-6 leading-relaxed">
                            Historical data suggests a 14-month lifecycle for this specific combination of litigation types.
                        </p>
                        <div className="flex justify-between items-end">
                            <span className="text-[10px] font-bold text-slate-400 uppercase">AVG DURATION</span>
                            <span className="text-xl font-bold text-slate-900 tracking-tight">425 Days</span>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-xl border border-slate-100 shadow-sm">
                        <div className="flex items-center justify-between mb-6">
                            <div className="w-10 h-10 bg-green-50 rounded-full flex items-center justify-center text-green-700">
                                <div className="w-5 h-6 border-2 border-green-700 rounded-sm relative">
                                    <div className="absolute inset-x-0 top-1/2 h-0.5 bg-green-700"></div>
                                </div>
                            </div>
                            <h3 className="text-sm font-bold text-slate-800 flex-grow ml-4">Risk Exposure</h3>
                        </div>
                        <p className="text-xs text-slate-500 mb-6 leading-relaxed">
                            Combined potential liability exposure exceeds current legal reserve allocations for Q4.
                        </p>
                        <div className="flex justify-between items-end">
                            <div className="flex flex-col">
                                <span className="text-[10px] font-bold text-slate-400 uppercase">RISK LEVEL</span>
                            </div>
                            <span className="text-xs font-bold text-orange-400 uppercase">ELEVATED</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CaseComparison;
