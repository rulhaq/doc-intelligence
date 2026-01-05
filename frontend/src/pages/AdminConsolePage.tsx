import { useState } from 'react'
import { Tab } from '@headlessui/react'
import {
  UsersIcon,
  CogIcon,
  ChartBarIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline'
import UserManagement from '../components/admin/UserManagement'
import SystemSettings from '../components/admin/SystemSettings'
import MonitoringDashboards from '../components/admin/MonitoringDashboards'
import DocumentManagement from '../components/admin/DocumentManagement'

const tabs = [
  { name: 'User Management', icon: UsersIcon, component: UserManagement },
  { name: 'System Settings', icon: CogIcon, component: SystemSettings },
  { name: 'Monitoring', icon: ChartBarIcon, component: MonitoringDashboards },
  { name: 'Documents', icon: DocumentTextIcon, component: DocumentManagement },
]

export default function AdminConsolePage() {
  const [selectedIndex, setSelectedIndex] = useState(0)

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Page Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Admin Console</h1>
            <p className="text-sm text-gray-600 mt-1">
              Manage users, configure settings, and monitor system health
            </p>
          </div>
          
          <div className="flex items-center gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-lg">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium text-green-700">System Operational</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tab.Group selectedIndex={selectedIndex} onChange={setSelectedIndex}>
        <div className="bg-white border-b border-gray-200 px-6">
          <Tab.List className="flex space-x-1">
            {tabs.map((tab) => (
              <Tab
                key={tab.name}
                className={({ selected }) =>
                  `flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all ${
                    selected
                      ? 'text-primary-600 border-b-2 border-primary-600 bg-primary-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`
                }
              >
                <tab.icon className="w-5 h-5" />
                {tab.name}
              </Tab>
            ))}
          </Tab.List>
        </div>

        <Tab.Panels className="flex-1 overflow-y-auto">
          {tabs.map((tab) => (
            <Tab.Panel key={tab.name} className="p-6">
              {tab.component && <tab.component />}
            </Tab.Panel>
          ))}
        </Tab.Panels>
      </Tab.Group>
    </div>
  )
}

