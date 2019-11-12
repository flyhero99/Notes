import Vue from 'vue'
import Router from 'vue-router'
import Index from '@/components/Index'
import Login from '@/components/Login'
import Test from '@/components/Test'
import PMI from '@/components/PMI'
import PosPMI from '@/components/PosPMI'
import PosPMIRiver from '@/components/PosPMIRiver'
import Search from '@/components/Search'
import CoSearch from '@/components/CoSearch'
import PhrasePMI from '@/components/PhrasePMI'
import WordCloud from '@/components/WordCloud'
import NotebookIndex from '@/components/notebook/Index'
import NotebookNotebook from '@/components/notebook/Notebook'
import EntryEditorIndex from '@/components/entryeditor/Index'
import EntryEditor from '@/components/entryeditor/EntryEditor'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Index',
      component: Index
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/test',
      name: 'Test',
      component: Test
    },
    {
      path: '/pmi',
      name: 'PMI',
      component: PMI
    },
    {
      path: '/pos_pmi_river',
      name: 'PosPMIRiver',
      component: PosPMIRiver
    },
    {
      path: '/pos_pmi',
      name: 'PosPMI',
      component: PosPMI
    },
    {
      path: '/search',
      name: 'Search',
      component: Search
    },
    {
      path: '/cosearch',
      name: 'CoSearch',
      component: CoSearch
    },
    {
      path: '/phrase_pmi',
      name: 'PhrasePMI',
      component: PhrasePMI
    },
    {
      path: '/cloud',
      name: 'WordCloud',
      component: WordCloud
    },
    {
      path: '/notebook/',
      name: 'NotebookIndex',
      component: NotebookIndex
    },
    {
      path: '/notebook/:id',
      name: 'NotebookNotebook',
      component: NotebookNotebook
    },
    {
      path: '/entryeditor/',
      name: 'EntryEditorIndex',
      component: EntryEditorIndex
    },
    {
      path: '/entryeditor/:id',
      name: 'EntryEditor',
      component: EntryEditor
    }
  ]
})
