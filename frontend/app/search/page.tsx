'use client'

import { useState } from 'react'
import SearchBar from '@/components/search/SearchBar'
import ResultsList from '@/components/search/ResultsList'
import { searchDocuments } from '@/lib/api-client'

export default function SearchPage() {
  const [results, setResults] = useState<any[]>([])
  const [searching, setSearching] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (query: string) => {
    if (!query.trim()) return

    setSearching(true)
    setSearched(true)
    
    try {
      const searchResults = await searchDocuments(query)
      setResults(searchResults)
    } catch (error) {
      console.error('Search error:', error)
      setResults([])
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Search Your Notes</h1>
      
      <SearchBar onSearch={handleSearch} searching={searching} />
      
      {searching && (
        <div className="text-center py-8">
          <p className="text-gray-500">Searching...</p>
        </div>
      )}
      
      {!searching && searched && (
        <ResultsList results={results} />
      )}
      
      {!searched && (
        <div className="text-center py-12 text-gray-500">
          <p>Enter a search query to find content in your documents</p>
        </div>
      )}
    </div>
  )
}