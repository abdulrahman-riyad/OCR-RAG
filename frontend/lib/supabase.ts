import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Helper functions for storage
export const uploadToSupabase = async (file: File, bucket: string = 'documents') => {
  const fileExt = file.name.split('.').pop()
  const fileName = `${Date.now()}-${Math.random().toString(36).substring(7)}.${fileExt}`
  
  const { data, error } = await supabase.storage
    .from(bucket)
    .upload(fileName, file)
  
  if (error) {
    throw error
  }
  
  return data
}

export const getPublicUrl = (path: string, bucket: string = 'documents') => {
  const { data } = supabase.storage
    .from(bucket)
    .getPublicUrl(path)
  
  return data.publicUrl
}