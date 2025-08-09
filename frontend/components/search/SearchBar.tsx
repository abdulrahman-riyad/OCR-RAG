'use client'

import { useState, useEffect, useRef } from 'react'
import { Search, X } from 'lucide-react'
import { getSearchSuggestions } from '@/lib/api-client'

interface SearchBarProps {
  onSearch: (query: string) => void
  searching: boolean
}

export default function SearchBar({ onSearch, searching }: SearchBarProps) {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const suggestionsRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.length >= 2) {
        try {
          const suggs = await getSearchSuggestions(query)
          setSuggestions(suggs)
          setShowSuggestions(true)
        } catch (error) {
          console.error('Error fetching suggestions:', error)
        }
      } else {
        setSuggestions([])
        setShowSuggestions(false)
      }
    }

    const debounceTimer = setTimeout(fetchSuggestions, 300)
    return () => clearTimeout(debounceTimer)
  }, [query])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(event.target as Node)) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query)
      setShowSuggestions(false)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion)
    setShowSuggestions(false)
    onSearch(suggestion)
  }

  return (
    <form onSubmit={handleSubmit} className="mb-8 relative">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
            placeholder="Search for equations, concepts, diagrams, or any text..."
            className="input pl-10 pr-10"
            disabled={searching}
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          
          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery('')
                setSuggestions([])
                setShowSuggestions(false)
              }}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X size={20} />
            </button>
          )}
          
          {/* Suggestions dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <div
              ref={suggestionsRef}
              className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-md shadow-lg z-10"
            >
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-4 py-2 hover:bg-gray-50 text-sm"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>
        
        <button
          type="submit"
          disabled={searching || !query.trim()}
          className="btn-primary flex items-center gap-2"
        >
          {searching ? (
            <>Searching...</>
          ) : (
            <>
              <Search size={20} />
              Search
            </>
          )}
        </button>
      </div>
      
      <div className="mt-2 flex gap-2 text-sm">
        <span className="text-gray-500">Try:</span>
        {['equation', 'circuit diagram', 'algorithm'].map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => setQuery(example)}
            className="text-blue-600 hover:underline"
          >
            {example}
          </button>
        ))}
      </div>
    </form>
  )
}