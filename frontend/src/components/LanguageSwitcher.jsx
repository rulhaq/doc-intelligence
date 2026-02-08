import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { GlobeAltIcon } from '@heroicons/react/24/outline';

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  useEffect(() => {
    const currentLang = i18n.language || 'en';
    document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = currentLang;
  }, [i18n.language]);

  const toggleLanguage = () => {
    const newLang = i18n.language === 'ar' ? 'en' : 'ar';
    i18n.changeLanguage(newLang);
    document.documentElement.dir = newLang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = newLang;
    // Force re-render by reloading the page to ensure all components update
    window.location.reload();
  };

  const isRTL = document.documentElement.dir === 'rtl';

  return (
    <button
      onClick={toggleLanguage}
      className={`flex items-center ${isRTL ? 'space-x-reverse space-x-2' : 'space-x-2'} px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors`}
      title={i18n.language === 'ar' ? 'Switch to English' : 'التبديل إلى العربية'}
    >
      <GlobeAltIcon className="h-5 w-5" />
      <span className="font-bold">{i18n.language === 'ar' ? 'EN' : 'AR'}</span>
    </button>
  );
};

export default LanguageSwitcher;
