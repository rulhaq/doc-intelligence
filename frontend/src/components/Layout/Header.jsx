import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
    MagnifyingGlassIcon,
    BellIcon,
    QuestionMarkCircleIcon,
    UserCircleIcon
} from '@heroicons/react/24/outline';
import LanguageSwitcher from '../LanguageSwitcher';

const Header = () => {
    const { t } = useTranslation();

    return (
        <header className="header">
            <div className="flex-1 max-w-xl">
                <div className="relative">
                    <div className={`pointer-events-none absolute inset-y-0 ${document.documentElement.dir === 'rtl' ? 'right-0 pr-3' : 'left-0 pl-3'} flex items-center`}>
                        <MagnifyingGlassIcon className="h-5 w-5 text-slate-300" aria-hidden="true" />
                    </div>
                    <input
                        type="text"
                        className={`block w-full rounded-md border-0 bg-slate-50 py-1.5 ${document.documentElement.dir === 'rtl' ? 'pr-10 pl-3' : 'pl-10 pr-3'} text-slate-900 ring-1 ring-inset ring-slate-100 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-red-600 sm:text-sm sm:leading-6`}
                        placeholder={t('common.searchPlaceholder')}
                    />
                </div>
            </div>

            <div className="flex items-center space-x-4">
                <div className={`flex space-x-2 text-sm font-medium ${document.documentElement.dir === 'rtl' ? 'border-l border-slate-200 pl-4 ml-2' : 'border-r border-slate-200 pr-4 mr-2'}`}>
                    <NavLink to="/" className={({ isActive }) => `px-2 py-1 ${isActive ? 'text-red-700 font-bold border-b-2 border-red-700' : 'text-slate-500 hover:text-slate-900'}`}>{t('common.dashboard')}</NavLink>
                    <NavLink to="/intelligence" className={({ isActive }) => `px-2 py-1 ${isActive ? 'text-red-700 font-bold border-b-2 border-red-700' : 'text-slate-500 hover:text-slate-900'}`}>{t('common.intelligence')}</NavLink>
                    <NavLink to="/reports" className={({ isActive }) => `px-2 py-1 ${isActive ? 'text-red-700 font-bold border-b-2 border-red-700' : 'text-slate-500 hover:text-slate-900'}`}>{t('common.reports')}</NavLink>
                    <NavLink to="/settings" className={({ isActive }) => `px-2 py-1 ${isActive ? 'text-red-700 font-bold border-b-2 border-red-700' : 'text-slate-500 hover:text-slate-900'}`}>{t('common.settings')}</NavLink>
                </div>

                <LanguageSwitcher />

                <button className="text-slate-400 hover:text-slate-500">
                    <BellIcon className="h-6 w-6" aria-hidden="true" />
                </button>
                <button className="text-slate-400 hover:text-slate-500">
                    <QuestionMarkCircleIcon className="h-6 w-6" aria-hidden="true" />
                </button>
                <div className="flex items-center">
                    <div className="h-8 w-8 rounded-full bg-slate-200 overflow-hidden border border-slate-300">
                        <img src="https://ui-avatars.com/api/?name=User&background=random" alt="User" />
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
