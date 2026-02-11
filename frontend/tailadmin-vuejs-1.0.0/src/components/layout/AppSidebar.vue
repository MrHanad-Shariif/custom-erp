<template>
  <aside
    :class="[
      'fixed mt-16 flex flex-col lg:mt-0 top-0 px-5 left-0 bg-white dark:bg-gray-900 dark:border-gray-800 text-gray-900 h-screen transition-all duration-300 ease-in-out z-99999 border-r border-gray-200',
      {
        'lg:w-[290px]': isExpanded || isMobileOpen || isHovered,
        'lg:w-[90px]': !isExpanded && !isHovered,
        'translate-x-0 w-[290px]': isMobileOpen,
        '-translate-x-full': !isMobileOpen,
        'lg:translate-x-0': true,
      },
    ]"
    @mouseenter="!isExpanded && (isHovered = true)"
    @mouseleave="isHovered = false"
  >
    <div
      :class="[
        'py-8 flex',
        !isExpanded && !isHovered ? 'lg:justify-center' : 'justify-start',
      ]"
    >
      <router-link to="/" class="flex items-center gap-2 no-underline">
        <template v-if="isExpanded || isHovered || isMobileOpen">
          <span class="text-xl font-bold text-gray-900 dark:text-white">Halabuur-ERP</span>
        </template>
        <template v-else>
          <span class="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-500 text-sm font-bold text-white">H</span>
        </template>
      </router-link>
    </div>
    <div
      class="flex flex-col overflow-y-auto duration-300 ease-linear no-scrollbar"
    >
      <nav class="mb-6">
        <div class="flex flex-col gap-4">
          <div v-for="(menuGroup, groupIndex) in menuGroups" :key="groupIndex">
            <h2
              :class="[
                'mb-4 text-xs uppercase flex leading-[20px] text-gray-400',
                !isExpanded && !isHovered
                  ? 'lg:justify-center'
                  : 'justify-start',
              ]"
            >
              <template v-if="isExpanded || isHovered || isMobileOpen">
                {{ menuGroup.title }}
              </template>
              <HorizontalDots v-else />
            </h2>
            <ul class="flex flex-col gap-4">
              <li v-for="(item, index) in menuGroup.items" :key="item.name">
                <button
                  v-if="item.subItems"
                  @click="toggleSubmenu(groupIndex, index)"
                  :class="[
                    'menu-item group w-full',
                    {
                      'menu-item-active': isSubmenuOpen(groupIndex, index),
                      'menu-item-inactive': !isSubmenuOpen(groupIndex, index),
                    },
                    !isExpanded && !isHovered
                      ? 'lg:justify-center'
                      : 'lg:justify-start',
                  ]"
                >
                  <span
                    :class="[
                      isSubmenuOpen(groupIndex, index)
                        ? 'menu-item-icon-active'
                        : 'menu-item-icon-inactive',
                    ]"
                  >
                    <component :is="item.icon" />
                  </span>
                  <span
                    v-if="isExpanded || isHovered || isMobileOpen"
                    class="menu-item-text"
                    >{{ item.name }}</span
                  >
                  <ChevronDownIcon
                    v-if="isExpanded || isHovered || isMobileOpen"
                    :class="[
                      'ml-auto w-5 h-5 transition-transform duration-200',
                      {
                        'rotate-180 text-brand-500': isSubmenuOpen(
                          groupIndex,
                          index
                        ),
                      },
                    ]"
                  />
                </button>
                <router-link
                  v-else-if="item.path"
                  :to="item.path"
                  :class="[
                    'menu-item group',
                    {
                      'menu-item-active': isActive(item.path),
                      'menu-item-inactive': !isActive(item.path),
                    },
                  ]"
                >
                  <span
                    :class="[
                      isActive(item.path)
                        ? 'menu-item-icon-active'
                        : 'menu-item-icon-inactive',
                    ]"
                  >
                    <component :is="item.icon" />
                  </span>
                  <span
                    v-if="isExpanded || isHovered || isMobileOpen"
                    class="menu-item-text"
                    >{{ item.name }}</span
                  >
                </router-link>
                <transition
                  @enter="startTransition"
                  @after-enter="endTransition"
                  @before-leave="startTransition"
                  @after-leave="endTransition"
                >
                  <div
                    v-show="
                      isSubmenuOpen(groupIndex, index) &&
                      (isExpanded || isHovered || isMobileOpen)
                    "
                  >
                    <ul class="mt-2 space-y-1 ml-9">
                      <li v-for="subItem in item.subItems" :key="subItem.name">
                        <router-link
                          :to="subItem.path"
                          :class="[
                            'menu-dropdown-item',
                            {
                              'menu-dropdown-item-active': isActive(
                                subItem.path
                              ),
                              'menu-dropdown-item-inactive': !isActive(
                                subItem.path
                              ),
                            },
                          ]"
                        >
                          {{ subItem.name }}
                          <span class="flex items-center gap-1 ml-auto">
                            <span
                              v-if="subItem.new"
                              :class="[
                                'menu-dropdown-badge',
                                {
                                  'menu-dropdown-badge-active': isActive(
                                    subItem.path
                                  ),
                                  'menu-dropdown-badge-inactive': !isActive(
                                    subItem.path
                                  ),
                                },
                              ]"
                            >
                              new
                            </span>
                            <span
                              v-if="subItem.pro"
                              :class="[
                                'menu-dropdown-badge',
                                {
                                  'menu-dropdown-badge-active': isActive(
                                    subItem.path
                                  ),
                                  'menu-dropdown-badge-inactive': !isActive(
                                    subItem.path
                                  ),
                                },
                              ]"
                            >
                              pro
                            </span>
                          </span>
                        </router-link>
                      </li>
                    </ul>
                  </div>
                </transition>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      <SidebarWidget v-if="isExpanded || isHovered || isMobileOpen" />
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";

import {
  GridIcon,
  ChevronDownIcon,
  HorizontalDots,
  UserCircleIcon,
  TableIcon,
  TaskIcon,
  BoxCubeIcon,
  LayoutDashboardIcon,
  PieChartIcon,
  SettingsIcon,
} from "../../icons";
import SidebarWidget from "./SidebarWidget.vue";
import { useSidebar } from "@/composables/useSidebar";
import { useAuth } from "@/composables/useAuth";

const route = useRoute();
const { isExpanded, isMobileOpen, isHovered, openSubmenu } = useSidebar();
const { hasAnyPermission, initFromStorage } = useAuth();

const menuGroups = computed(() => {
  const groups = [];
  groups.push({
    title: "ERP",
    items: [
      {
        icon: GridIcon,
        name: "Dashboard",
        path: "/",
      },
      ...(hasAnyPermission("crm.view", "crm.edit")
        ? [
            {
              icon: TableIcon,
              name: "CRM",
              subItems: [
                { name: "Leads", path: "/crm/leads" },
                { name: "Customers", path: "/crm/customers" },
              ],
            },
          ]
        : []),
      ...(hasAnyPermission("hrm.view", "hrm.edit")
        ? [
            {
              icon: UserCircleIcon,
              name: "HRM",
              subItems: [
                { name: "Employees", path: "/hrm/employees" },
                { name: "Payroll", path: "/hrm/payroll" },
              ],
            },
          ]
        : []),
      ...(hasAnyPermission("inventory.view", "inventory.edit")
        ? [
            {
              icon: BoxCubeIcon,
              name: "Inventory",
              subItems: [
                { name: "Warehouses", path: "/inventory/warehouses" },
                { name: "SKUs", path: "/inventory/skus" },
                { name: "Stock", path: "/inventory/stock" },
                { name: "Purchase Orders", path: "/inventory/purchase-orders" },
              ],
            },
          ]
        : []),
      ...(hasAnyPermission("pm.view", "pm.edit")
        ? [
            {
              icon: TaskIcon,
              name: "Projects",
              subItems: [
                { name: "Projects", path: "/pm/projects" },
                { name: "Timesheets", path: "/pm/timesheets" },
              ],
            },
          ]
        : []),
      ...(hasAnyPermission("finance.view", "finance.edit")
        ? [
            {
              icon: PieChartIcon,
              name: "Finance",
              subItems: [{ name: "Invoices", path: "/finance/invoices" }],
            },
          ]
        : []),
      ...(hasAnyPermission("auth.view", "auth.edit")
        ? [
            {
              icon: SettingsIcon,
              name: "Authentication",
              subItems: [
                { name: "Users", path: "/auth/users" },
                { name: "Roles", path: "/auth/roles" },
              ],
            },
          ]
        : []),
    ].filter(Boolean),
  });
  return groups;
});

const isActive = (path) => route.path === path;

const toggleSubmenu = (groupIndex, itemIndex) => {
  const key = `${groupIndex}-${itemIndex}`;
  openSubmenu.value = openSubmenu.value === key ? null : key;
};

const isAnySubmenuRouteActive = computed(() => {
  const groups = menuGroups.value;
  return Array.isArray(groups) && groups.some((group) =>
    group.items?.some(
      (item) =>
        item.subItems && item.subItems.some((subItem) => isActive(subItem.path))
    )
  );
});

const isSubmenuOpen = (groupIndex, itemIndex) => {
  const key = `${groupIndex}-${itemIndex}`;
  const groups = menuGroups.value;
  const group = Array.isArray(groups) ? groups[groupIndex] : null;
  const item = group?.items?.[itemIndex];
  return (
    openSubmenu.value === key ||
    (isAnySubmenuRouteActive.value &&
      item?.subItems?.some((subItem) => isActive(subItem.path)))
  );
};

const startTransition = (el) => {
  el.style.height = "auto";
  const height = el.scrollHeight;
  el.style.height = "0px";
  el.offsetHeight; // force reflow
  el.style.height = height + "px";
};

const endTransition = (el) => {
  el.style.height = "";
};
</script>
